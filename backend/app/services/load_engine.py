from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Tuple
from app.models.academic import AcademicEvent
from app.models.training import TrainingSession
from app.models.lifestyle import SleepRecord, RecoveryCheckIn
from app.models.wearable import WearableObservation
from app.models.user import StudentProfile

class DualLoadEngine:
    """
    Transparent, configurable dual-load calculation engine.
    Estimates:
    - Academic Load Score (0-100)
    - Athletic Load Score (0-100)
    - Recovery Score (0-100)
    - Dual-Load Risk Score (0-100)
    - Data completeness and confidence indicator
    
    Disclaimer: Heuristic educational model for student self-awareness,
    not a medical diagnostic device.
    """

    # Configurable weights
    WEIGHT_ACADEMIC = 0.45
    WEIGHT_ATHLETIC = 0.40
    WEIGHT_RECOVERY_MODIFIER = 0.50

    @classmethod
    def calculate_for_user(cls, db: Session, user_id: int, target_date: date = None) -> Dict[str, Any]:
        if target_date is None:
            target_date = date.today()

        day_start = datetime.combine(target_date, datetime.min.time())
        day_end = datetime.combine(target_date, datetime.max.time())
        window_48h = day_end + timedelta(hours=48)
        past_7d = day_start - timedelta(days=7)

        profile = db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
        target_sleep = profile.usual_sleep_target_hours if profile else 8.0

        # 1. ACADEMIC LOAD CALCULATION
        academic_events = db.query(AcademicEvent).filter(
            AcademicEvent.user_id == user_id,
            AcademicEvent.start_time >= day_start,
            AcademicEvent.start_time <= day_end
        ).all()

        upcoming_exams_48h = db.query(AcademicEvent).filter(
            AcademicEvent.user_id == user_id,
            AcademicEvent.event_type.in_(["exam", "deadline"]),
            AcademicEvent.start_time >= day_start,
            AcademicEvent.start_time <= window_48h
        ).all()

        total_academic_hours = 0.0
        priority_weighted_hours = 0.0
        has_consecutive_long_block = False

        for ev in academic_events:
            duration_hrs = max(0.5, (ev.end_time - ev.start_time).total_seconds() / 3600.0)
            total_academic_hours += duration_hrs
            
            p_mult = 1.0
            if ev.priority == "critical":
                p_mult = 1.8
            elif ev.priority == "high":
                p_mult = 1.4
            elif ev.priority == "low":
                p_mult = 0.8
            
            priority_weighted_hours += duration_hrs * p_mult
            if duration_hrs >= 3.5:
                has_consecutive_long_block = True

        exam_proximity_boost = min(35.0, len(upcoming_exams_48h) * 18.0)
        base_academic_score = min(65.0, (priority_weighted_hours / 7.0) * 65.0)
        academic_load_score = min(100.0, base_academic_score + exam_proximity_boost + (8.0 if has_consecutive_long_block else 0.0))

        # 2. ATHLETIC LOAD CALCULATION
        training_sessions = db.query(TrainingSession).filter(
            TrainingSession.user_id == user_id,
            TrainingSession.start_time >= day_start,
            TrainingSession.start_time <= day_end
        ).all()

        past_week_sessions = db.query(TrainingSession).filter(
            TrainingSession.user_id == user_id,
            TrainingSession.start_time >= past_7d,
            TrainingSession.start_time <= day_end
        ).all()

        total_training_minutes = 0
        intensity_points = 0.0

        for ts in training_sessions:
            dur = ts.duration_minutes or 60
            total_training_minutes += dur
            
            mult = 0.5
            if ts.intensity == "all_out":
                mult = 1.2
            elif ts.intensity == "high":
                mult = 0.9
            elif ts.intensity == "light":
                mult = 0.3
            
            intensity_points += dur * mult

        weekly_frequency_bonus = min(15.0, len(past_week_sessions) * 2.5)
        athletic_load_score = min(100.0, (intensity_points / 75.0) * 85.0 + weekly_frequency_bonus)

        # 3. RECOVERY SCORE CALCULATION
        # Look for sleep records or wearable sleep
        sleep_record = db.query(SleepRecord).filter(
            SleepRecord.user_id == user_id,
            SleepRecord.sleep_end >= day_start - timedelta(hours=12),
            SleepRecord.sleep_end <= day_end
        ).order_by(SleepRecord.sleep_end.desc()).first()

        wearable_sleep = db.query(WearableObservation).filter(
            WearableObservation.user_id == user_id,
            WearableObservation.metric_type == "sleep_duration",
            WearableObservation.recorded_at >= day_start - timedelta(hours=12),
            WearableObservation.recorded_at <= day_end
        ).order_by(WearableObservation.recorded_at.desc()).first()

        actual_sleep_hours = None
        data_sources_available = []

        if sleep_record:
            actual_sleep_hours = sleep_record.duration_hours
            data_sources_available.append(f"Sleep Log ({sleep_record.data_source})")
        elif wearable_sleep:
            actual_sleep_hours = wearable_sleep.value
            data_sources_available.append("Wearable Sleep")

        # HRV observation
        hrv_obs = db.query(WearableObservation).filter(
            WearableObservation.user_id == user_id,
            WearableObservation.metric_type == "hrv",
            WearableObservation.recorded_at >= past_7d
        ).order_by(WearableObservation.recorded_at.desc()).first()

        if hrv_obs:
            data_sources_available.append("Wearable HRV")

        # Resting HR
        rhr_obs = db.query(WearableObservation).filter(
            WearableObservation.user_id == user_id,
            WearableObservation.metric_type == "resting_hr",
            WearableObservation.recorded_at >= past_7d
        ).order_by(WearableObservation.recorded_at.desc()).first()

        if rhr_obs:
            data_sources_available.append("Wearable Resting HR")

        # Subjective checkin
        checkin = db.query(RecoveryCheckIn).filter(
            RecoveryCheckIn.user_id == user_id,
            RecoveryCheckIn.created_at >= day_start,
            RecoveryCheckIn.created_at <= day_end
        ).order_by(RecoveryCheckIn.created_at.desc()).first()

        if checkin:
            data_sources_available.append("Fatigue Self-Check")

        # Compute recovery score
        if actual_sleep_hours is not None:
            sleep_ratio = actual_sleep_hours / max(5.0, target_sleep)
            sleep_component = min(100.0, sleep_ratio * 100.0)
        else:
            sleep_component = 70.0  # default baseline when missing

        hrv_component = 75.0
        if hrv_obs:
            # typical healthy HRV rMSSD is 45-80ms
            if hrv_obs.value >= 65:
                hrv_component = 92.0
            elif hrv_obs.value >= 50:
                hrv_component = 80.0
            elif hrv_obs.value >= 35:
                hrv_component = 60.0
            else:
                hrv_component = 40.0

        subjective_penalty = 0.0
        if checkin:
            # fatigue 1-10, muscle soreness 1-10
            combined_fatigue = (checkin.muscle_soreness + checkin.mental_fatigue) / 2.0
            if combined_fatigue >= 7:
                subjective_penalty = 22.0
            elif combined_fatigue >= 5:
                subjective_penalty = 12.0

        raw_recovery = (sleep_component * 0.55) + (hrv_component * 0.45) - subjective_penalty
        recovery_score = max(10.0, min(100.0, raw_recovery))

        # 4. CONFIDENCE SCORE
        confidence_base = 50.0
        if actual_sleep_hours is not None:
            confidence_base += 20.0
        if hrv_obs:
            confidence_base += 15.0
        if rhr_obs:
            confidence_base += 10.0
        if checkin:
            confidence_base += 5.0
        confidence_score = min(98.0, confidence_base)

        # 5. DUAL-LOAD RISK SCORE
        # High academic load + high athletic load + depleted recovery = peak risk
        combined_load = (academic_load_score * cls.WEIGHT_ACADEMIC) + (athletic_load_score * cls.WEIGHT_ATHLETIC)
        # Low recovery amplifies load stress
        recovery_deficit_factor = 1.0 + ((100.0 - recovery_score) / 100.0) * cls.WEIGHT_RECOVERY_MODIFIER
        dual_load_risk_score = min(100.0, max(0.0, (combined_load / 85.0) * 100.0 * (recovery_deficit_factor / 1.25)))

        # 6. RISK LEVEL
        if dual_load_risk_score >= 70.0:
            risk_level = "RED"
        elif dual_load_risk_score >= 42.0:
            risk_level = "YELLOW"
        else:
            risk_level = "GREEN"

        # 7. FACTORS CONTRIBUTING
        factors: List[Dict[str, Any]] = []
        if len(upcoming_exams_48h) > 0:
            factors.append({
                "name": "Upcoming Exam / Deadline Proximity",
                "impact": "negative",
                "description": f"{len(upcoming_exams_48h)} high-stakes academic deadline(s) within next 48 hours",
                "weight": 0.35
            })
        if total_academic_hours >= 5.0:
            factors.append({
                "name": "High Scheduled Academic Hours",
                "impact": "negative",
                "description": f"{total_academic_hours:.1f} hours of planned coursework and study sessions today",
                "weight": 0.25
            })
        if total_training_minutes >= 60:
            factors.append({
                "name": "Significant Athletic Demands",
                "impact": "negative",
                "description": f"{total_training_minutes} minutes of athletic training planned",
                "weight": 0.20
            })
        if recovery_score < 60:
            factors.append({
                "name": "Suppressed Physiological Recovery",
                "impact": "negative",
                "description": f"Recovery score is {recovery_score:.0f}/100. Deficit in sleep or elevated nervous system fatigue.",
                "weight": 0.30
            })
        elif recovery_score >= 80:
            factors.append({
                "name": "Optimal Physiological Readiness",
                "impact": "positive",
                "description": f"Recovery score is strong ({recovery_score:.0f}/100). Baseline HRV and sleep duration are supportive.",
                "weight": 0.25
            })

        return {
            "academic_load_score": round(academic_load_score, 1),
            "athletic_load_score": round(athletic_load_score, 1),
            "recovery_score": round(recovery_score, 1),
            "dual_load_risk_score": round(dual_load_risk_score, 1),
            "risk_level": risk_level,
            "confidence_score": round(confidence_score, 1),
            "factors": factors,
            "data_sources_available": data_sources_available,
            "target_date": target_date
        }
