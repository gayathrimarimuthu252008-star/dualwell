from datetime import datetime, timedelta, date, time
from sqlalchemy.orm import Session
from app.database import SessionLocal, Base, engine
from app.models.user import User, StudentProfile, PrivacyPreference
from app.models.wearable import WearableConnection, WearableObservation
from app.models.academic import AcademicEvent
from app.models.training import TrainingSession
from app.models.lifestyle import MealLog, HydrationLog, SleepRecord, RecoveryCheckIn
from app.models.load_risk import DailyLoadSnapshot, RiskAssessment
from app.models.notification import Reminder
from app.core.security import hash_password
import json

def seed_database():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == "alex.morgan@dualwell.edu").first()
        if existing_user:
            return

        # 1. Create Demo Student User
        user = User(
            email="alex.morgan@dualwell.edu",
            hashed_password=hash_password("DualWell2026!"),
            full_name="Alex Morgan",
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # 2. Student Profile
        profile = StudentProfile(
            user_id=user.id,
            age_range="20-22",
            major="Computer Science & Bioengineering",
            primary_sport="Collegiate Rowing / Middle-Distance Running",
            usual_sleep_target_hours=8.0,
            usual_bedtime="23:00",
            usual_wake_time="07:00",
            daily_hydration_goal_ml=2800,
            training_days_per_week=5,
            academic_goals="Maintain 3.8+ GPA in Computer Science while maintaining peak VO2max for spring championships."
        )
        db.add(profile)

        # 3. Privacy Preference
        privacy = PrivacyPreference(
            user_id=user.id,
            consent_wearable_sync=True,
            share_anonymous_metrics=False,
            allow_overload_notifications=True,
            allow_hydration_nudges=True,
            quiet_hours_enabled=True,
            quiet_hours_start="22:30",
            quiet_hours_end="06:30"
        )
        db.add(privacy)

        now = datetime.utcnow()
        today = date.today()

        # 4. Academic Events
        events = [
            AcademicEvent(
                user_id=user.id,
                title="Advanced Algorithms Final Exam",
                event_type="exam",
                course_name="CS 301",
                start_time=datetime.combine(today + timedelta(days=2), time(9, 0)),
                end_time=datetime.combine(today + timedelta(days=2), time(12, 0)),
                priority="critical",
                estimated_workload_hours=3.0,
                is_fixed=True,
                is_completed=False,
                notes="Covers dynamic programming, graph algorithms, and NP-completeness."
            ),
            AcademicEvent(
                user_id=user.id,
                title="Distributed Systems Lab 3 Submission",
                event_type="deadline",
                course_name="CS 340",
                start_time=datetime.combine(today + timedelta(days=1), time(17, 0)),
                end_time=datetime.combine(today + timedelta(days=1), time(17, 0)),
                priority="high",
                estimated_workload_hours=4.0,
                is_fixed=True,
                is_completed=False,
                notes="Raft consensus implementation and fault tolerance test suite."
            ),
            AcademicEvent(
                user_id=user.id,
                title="Database Systems Architecture Lecture",
                event_type="class",
                course_name="CS 320",
                start_time=datetime.combine(today, time(10, 0)),
                end_time=datetime.combine(today, time(11, 30)),
                priority="medium",
                estimated_workload_hours=1.5,
                is_fixed=True,
                is_completed=True,
                notes="Query optimization, B+ Tree indexing."
            ),
            AcademicEvent(
                user_id=user.id,
                title="Algorithms Problem Set & Proof Revision",
                event_type="study_session",
                course_name="CS 301",
                start_time=datetime.combine(today, time(14, 0)),
                end_time=datetime.combine(today, time(17, 0)),
                priority="high",
                estimated_workload_hours=3.0,
                is_fixed=False,
                is_completed=False,
                notes="Work through past final exam problem sets 2023-2025."
            )
        ]
        db.add_all(events)

        # 5. Training Sessions
        trainings = [
            TrainingSession(
                user_id=user.id,
                title="Rowing Ergometer Interval Pyramids (5x1000m)",
                activity_type="rowing",
                start_time=datetime.combine(today, time(17, 30)),
                end_time=datetime.combine(today, time(18, 45)),
                duration_minutes=75,
                intensity="high",
                avg_heart_rate=162.0,
                max_heart_rate=184.0,
                perceived_exertion=8,
                is_flexible=True,
                notes="Anaerobic threshold intervals. Pace 1:44/500m."
            ),
            TrainingSession(
                user_id=user.id,
                title="Strength & Core Conditioning",
                activity_type="strength",
                start_time=datetime.combine(today + timedelta(days=1), time(7, 0)),
                end_time=datetime.combine(today + timedelta(days=1), time(8, 0)),
                duration_minutes=60,
                intensity="moderate",
                avg_heart_rate=128.0,
                max_heart_rate=152.0,
                perceived_exertion=6,
                is_flexible=True,
                notes="Squats, romanian deadlifts, pull-ups, posterior chain stability."
            )
        ]
        db.add_all(trainings)

        # 6. Wearable Connection & Observations
        conn = WearableConnection(
            user_id=user.id,
            provider="demo",
            display_name="DualWell Athlete Simulator (Demo Engine)",
            is_connected=True,
            last_synced_at=now - timedelta(minutes=10),
            sync_status="success"
        )
        db.add(conn)

        observations = [
            WearableObservation(
                user_id=user.id,
                provider="demo",
                metric_type="heart_rate",
                value=64.0,
                unit="bpm",
                recorded_at=now - timedelta(minutes=15),
                data_source="SIMULATED_DEMO",
                extra_metadata="Midday resting observation"
            ),
            WearableObservation(
                user_id=user.id,
                provider="demo",
                metric_type="hrv",
                value=62.5,
                unit="ms",
                recorded_at=now - timedelta(hours=5),
                data_source="SIMULATED_DEMO",
                extra_metadata="Overnight rMSSD baseline"
            ),
            WearableObservation(
                user_id=user.id,
                provider="demo",
                metric_type="resting_hr",
                value=53.0,
                unit="bpm",
                recorded_at=now - timedelta(hours=6),
                data_source="SIMULATED_DEMO",
                extra_metadata="Lowest sleeping heart rate"
            ),
            WearableObservation(
                user_id=user.id,
                provider="demo",
                metric_type="steps",
                value=9450.0,
                unit="count",
                recorded_at=now,
                data_source="SIMULATED_DEMO",
                extra_metadata="Active campus transit"
            ),
            WearableObservation(
                user_id=user.id,
                provider="demo",
                metric_type="sleep_duration",
                value=7.6,
                unit="hours",
                recorded_at=now - timedelta(hours=8),
                data_source="SIMULATED_DEMO",
                extra_metadata="Deep: 1.7h, REM: 1.8h, Light: 4.1h"
            ),
            WearableObservation(
                user_id=user.id,
                provider="demo",
                metric_type="recovery_score",
                value=82.0,
                unit="score",
                recorded_at=now - timedelta(hours=5),
                data_source="SIMULATED_DEMO",
                extra_metadata="High autonomic recovery"
            )
        ]
        db.add_all(observations)

        # 7. Sleep Record
        sleep = SleepRecord(
            user_id=user.id,
            sleep_start=datetime.combine(today - timedelta(days=1), time(23, 15)),
            sleep_end=datetime.combine(today, time(6, 50)),
            duration_hours=7.6,
            deep_sleep_hours=1.7,
            rem_sleep_hours=1.8,
            light_sleep_hours=4.1,
            awake_minutes=15,
            efficiency_percentage=89.0,
            data_source="SIMULATED_DEMO",
            notes="Woke feeling refreshed; good sleep latency."
        )
        db.add(sleep)

        # 8. Meals and Hydration
        meals = [
            MealLog(
                user_id=user.id,
                meal_type="Breakfast",
                description="Steel-cut oatmeal with blueberries, chia seeds, whey protein isolate, and almond butter",
                logged_at=datetime.combine(today, time(7, 30)),
                portion_size="Large",
                calories=620,
                protein_g=38.0,
                carbs_g=72.0,
                fat_g=18.0
            ),
            MealLog(
                user_id=user.id,
                meal_type="Lunch",
                description="Grilled chicken breast grain bowl with quinoa, roasted sweet potatoes, and avocado",
                logged_at=datetime.combine(today, time(12, 15)),
                portion_size="Large",
                calories=780,
                protein_g=48.0,
                carbs_g=85.0,
                fat_g=22.0
            )
        ]
        db.add_all(meals)

        hydrations = [
            HydrationLog(user_id=user.id, amount_ml=500, logged_at=datetime.combine(today, time(7, 45))),
            HydrationLog(user_id=user.id, amount_ml=500, logged_at=datetime.combine(today, time(10, 30))),
            HydrationLog(user_id=user.id, amount_ml=400, logged_at=datetime.combine(today, time(12, 30))),
            HydrationLog(user_id=user.id, amount_ml=450, logged_at=datetime.combine(today, time(14, 15)))
        ]
        db.add_all(hydrations)

        # 9. Past 7 days Daily Load Snapshots for instant trend visualization
        for i in range(7):
            d = today - timedelta(days=(6 - i))
            acad_score = 45.0 + (i * 5) % 35
            ath_score = 50.0 + (i * 7) % 40
            rec_score = 70.0 + (i * 3) % 25
            dual_score = round((acad_score * 0.45 + ath_score * 0.40) * (1.0 + (100 - rec_score) / 250.0), 1)
            level = "GREEN" if dual_score < 42 else ("YELLOW" if dual_score < 70 else "RED")
            
            snap = DailyLoadSnapshot(
                user_id=user.id,
                snapshot_date=d,
                academic_load_score=round(acad_score, 1),
                athletic_load_score=round(ath_score, 1),
                recovery_score=round(rec_score, 1),
                dual_load_risk_score=dual_score,
                risk_level=level,
                confidence_score=90.0,
                factors_json=json.dumps([{"name": "Regular study and training", "impact": "neutral", "description": "Standard term load", "weight": 0.2}])
            )
            db.add(snap)

        # 10. Initial Risk Assessment
        risk_assess = RiskAssessment(
            user_id=user.id,
            risk_level="YELLOW",
            risk_score=54.2,
            academic_component=62.0,
            athletic_component=65.0,
            recovery_component=78.0,
            factors_summary="Elevated academic load due to Algorithms Final in 48 hours paired with high-intensity rowing intervals.",
            recommended_actions=json.dumps([
                "Cap intense training intervals today and avoid extra volume.",
                "Ensure steady hydration and consume complex carbs before evening study.",
                "Protect an 8-hour sleep window tonight."
            ]),
            calculated_at=now
        )
        db.add(risk_assess)

        # 11. Initial Smart Reminders
        reminders = [
            Reminder(
                user_id=user.id,
                title="Hydration Refuel",
                message="You are 950 mL away from your 2800 mL target. Drink a 350 mL glass before afternoon study.",
                category="HYDRATION",
                scheduled_time=datetime.combine(today, time(15, 30))
            ),
            Reminder(
                user_id=user.id,
                title="Pre-Training Fuel & Mobility",
                message="Rowing intervals start at 5:30 PM. Complete hip/thoracic warm-up and take light carbohydrates.",
                category="TRAINING",
                scheduled_time=datetime.combine(today, time(17, 10))
            ),
            Reminder(
                user_id=user.id,
                title="Algorithms Study Break",
                message="Take a 15-minute screen-free mental pause to facilitate memory consolidation.",
                category="STUDY_BREAK",
                scheduled_time=datetime.combine(today, time(15, 30))
            )
        ]
        db.add_all(reminders)

        db.commit()
        print("Demo database successfully initialized with collegiate athlete 'Alex Morgan'!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
