from datetime import datetime, timedelta, time
from sqlalchemy.orm import Session
from typing import List
from app.models.academic import AcademicEvent
from app.models.training import TrainingSession
from app.models.scheduler import ScheduleRecommendation
from app.models.user import StudentProfile

class DynamicSchedulerEngine:
    """
    Intelligent schedule recommendation engine.
    - Preserves fixed commitments (exams, mandatory lectures).
    - Detects overlapping conflicts.
    - Moves flexible study sessions or training workouts out of sleep windows.
    - Inserts nutrition, hydration, and cognitive recovery buffers.
    - Generates actionable recommendations with clear rationales.
    - Never mutates events silently; requires student confirmation.
    """

    @classmethod
    def generate_recommendations(cls, db: Session, user_id: int) -> List[ScheduleRecommendation]:
        now = datetime.utcnow()
        horizon_end = now + timedelta(days=2)

        profile = db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
        bedtime_str = profile.usual_bedtime if profile else "23:00"
        waketime_str = profile.usual_wake_time if profile else "07:00"

        # Parse sleep hours
        bed_h, bed_m = map(int, bedtime_str.split(":"))
        wake_h, wake_m = map(int, waketime_str.split(":"))

        academic_events = db.query(AcademicEvent).filter(
            AcademicEvent.user_id == user_id,
            AcademicEvent.start_time >= now - timedelta(hours=2),
            AcademicEvent.start_time <= horizon_end,
            AcademicEvent.is_completed == False
        ).order_by(AcademicEvent.start_time.asc()).all()

        training_sessions = db.query(TrainingSession).filter(
            TrainingSession.user_id == user_id,
            TrainingSession.start_time >= now - timedelta(hours=2),
            TrainingSession.start_time <= horizon_end
        ).order_by(TrainingSession.start_time.asc()).all()

        recommendations: List[ScheduleRecommendation] = []

        # 1. Check for Direct Time Conflicts between Academic and Training
        for ac in academic_events:
            for tr in training_sessions:
                # overlap check
                if ac.start_time < tr.end_time and tr.start_time < ac.end_time:
                    # Conflict found!
                    if ac.is_fixed and tr.is_flexible:
                        # Move flexible training session after academic event + 30 min buffer
                        proposed_start = ac.end_time + timedelta(minutes=30)
                        proposed_end = proposed_start + timedelta(minutes=tr.duration_minutes)
                        
                        rec = ScheduleRecommendation(
                            user_id=user_id,
                            related_event_id=tr.id,
                            event_title=tr.title,
                            event_category="training",
                            original_start_time=tr.start_time,
                            original_end_time=tr.end_time,
                            proposed_start_time=proposed_start,
                            proposed_end_time=proposed_end,
                            action_type="SHIFT_TIME",
                            rationale=(
                                f"Direct scheduling clash with fixed academic event '{ac.title}'. "
                                f"Moved training to {proposed_start.strftime('%I:%M %p')} with a 30-minute transition buffer."
                            ),
                            status="pending"
                        )
                        recommendations.append(rec)
                    elif not ac.is_fixed and not tr.is_flexible:
                        # Move flexible academic study block
                        proposed_start = tr.end_time + timedelta(minutes=45)
                        dur = ac.end_time - ac.start_time
                        proposed_end = proposed_start + dur
                        
                        rec = ScheduleRecommendation(
                            user_id=user_id,
                            related_event_id=ac.id,
                            event_title=ac.title,
                            event_category="academic",
                            original_start_time=ac.start_time,
                            original_end_time=ac.end_time,
                            proposed_start_time=proposed_start,
                            proposed_end_time=proposed_end,
                            action_type="SHIFT_TIME",
                            rationale=(
                                f"Overlaps with high-priority training session '{tr.title}'. "
                                f"Rescheduled study session after workout and cool-down window."
                            ),
                            status="pending"
                        )
                        recommendations.append(rec)

        # 2. Check for Study or Training during Sleep Hours
        for ac in academic_events:
            if not ac.is_fixed:
                if ac.end_time.hour >= bed_h or ac.start_time.hour >= bed_h or ac.start_time.hour < wake_h:
                    # Shift earlier to afternoon / early evening
                    target_date = ac.start_time.date()
                    proposed_start = datetime.combine(target_date, time(16, 0))  # 4:00 PM
                    proposed_end = proposed_start + (ac.end_time - ac.start_time)
                    
                    rec = ScheduleRecommendation(
                        user_id=user_id,
                        related_event_id=ac.id,
                        event_title=ac.title,
                        event_category="academic",
                        original_start_time=ac.start_time,
                        original_end_time=ac.end_time,
                        proposed_start_time=proposed_start,
                        proposed_end_time=proposed_end,
                        action_type="EARLY_WINDDOWN",
                        rationale=(
                            f"Study block '{ac.title}' encroaches on your target bedtime ({bedtime_str}). "
                            "Shifted to 4:00 PM to safeguard restorative sleep and memory consolidation."
                        ),
                        status="pending"
                    )
                    recommendations.append(rec)

        # 3. Insert Cognitive Break for long study sessions (> 2.5 hours)
        for ac in academic_events:
            dur_hours = (ac.end_time - ac.start_time).total_seconds() / 3600.0
            if dur_hours >= 2.5 and not ac.is_fixed:
                break_start = ac.start_time + timedelta(minutes=90)
                break_end = break_start + timedelta(minutes=20)
                rec = ScheduleRecommendation(
                    user_id=user_id,
                    related_event_id=ac.id,
                    event_title="Recovery & Hydration Buffer",
                    event_category="break",
                    original_start_time=ac.start_time,
                    original_end_time=ac.end_time,
                    proposed_start_time=break_start,
                    proposed_end_time=break_end,
                    action_type="INSERT_REST",
                    rationale=(
                        f"Long continuous block ({dur_hours:.1f}h) detected in '{ac.title}'. "
                        "Inserted a 20-minute cognitive reset buffer with water replenishment."
                    ),
                    status="pending"
                )
                recommendations.append(rec)

        # Persist pending recommendations that don't duplicate
        existing_recs = db.query(ScheduleRecommendation).filter(
            ScheduleRecommendation.user_id == user_id,
            ScheduleRecommendation.status == "pending"
        ).all()
        existing_keys = { (r.event_title, r.action_type) for r in existing_recs }

        added_recs = []
        for r in recommendations:
            if (r.event_title, r.action_type) not in existing_keys:
                db.add(r)
                added_recs.append(r)
        
        db.commit()
        for r in added_recs:
            db.refresh(r)
        
        # Return all pending recommendations
        return db.query(ScheduleRecommendation).filter(
            ScheduleRecommendation.user_id == user_id,
            ScheduleRecommendation.status == "pending"
        ).all()

    @classmethod
    def apply_recommendation(cls, db: Session, user_id: int, rec_id: int) -> bool:
        rec = db.query(ScheduleRecommendation).filter(
            ScheduleRecommendation.id == rec_id,
            ScheduleRecommendation.user_id == user_id
        ).first()

        if not rec or rec.status != "pending":
            return False

        if rec.related_event_id:
            if rec.event_category == "academic":
                ac = db.query(AcademicEvent).filter(AcademicEvent.id == rec.related_event_id).first()
                if ac:
                    ac.start_time = rec.proposed_start_time
                    ac.end_time = rec.proposed_end_time
            elif rec.event_category == "training":
                tr = db.query(TrainingSession).filter(TrainingSession.id == rec.related_event_id).first()
                if tr:
                    tr.start_time = rec.proposed_start_time
                    tr.end_time = rec.proposed_end_time

        rec.status = "accepted"
        db.commit()
        return True

    @classmethod
    def reject_recommendation(cls, db: Session, user_id: int, rec_id: int) -> bool:
        rec = db.query(ScheduleRecommendation).filter(
            ScheduleRecommendation.id == rec_id,
            ScheduleRecommendation.user_id == user_id
        ).first()

        if not rec:
            return False

        rec.status = "rejected"
        db.commit()
        return True
