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
from app.services.risk_prediction import risk_predictor
import json

DEMO_EMAIL = "alex.morgan@dualwell.edu"


def _delete_demo_user_data(db: Session, user_id: int) -> None:
    """Removes every row belonging to the demo user (children first, then the user)."""
    for model in (
        Reminder, MealLog, HydrationLog, SleepRecord, RecoveryCheckIn,
        TrainingSession, AcademicEvent, WearableObservation, WearableConnection,
        DailyLoadSnapshot, RiskAssessment, StudentProfile, PrivacyPreference,
    ):
        db.query(model).filter(model.user_id == user_id).delete(synchronize_session=False)
    db.query(User).filter(User.id == user_id).delete(synchronize_session=False)
    db.commit()


def seed_database(reseed: bool = False, db: Session = None):
    """Seeds the Alex Morgan demo persona, always relative to today's date.

    With ``reseed=True`` any existing demo user and their records are deleted
    and regenerated. An optional ``db`` session can be injected (used by tests).
    """
    owns_session = db is None
    if owns_session:
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()

    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == DEMO_EMAIL).first()
        if existing_user:
            if not reseed:
                print("Demo user already exists; skipping seed (use --reseed to regenerate).")
                return
            _delete_demo_user_data(db, existing_user.id)
            db.expunge(existing_user)  # detach stale identity before re-inserting user id 1
            print(f"Existing demo data wiped; regenerating relative to {date.today().isoformat()}...")

        # 1. Create Demo Student User
        user = User(
            email=DEMO_EMAIL,
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

        # 7. Sleep Records - one per night across the reporting window so the
        #    7-day sleep chart and weekly consistency metrics read real history.
        #    Stages, awake time and efficiency are derived from the time in bed
        #    so the numbers stay internally consistent.
        sleep_nights = [
            # (nights ago, lights out, wake up, asleep hours, note)
            (7, time(23, 40), time(7, 5), 7.0, "Late lab write-up; slow onset."),
            (6, time(23, 5), time(7, 10), 7.8, "Consistent bedtime, restorative night."),
            (5, time(23, 50), time(6, 45), 6.6, "Short night before exam revision."),
            (4, time(22, 55), time(7, 5), 7.8, "Woke refreshed; high next-day readiness."),
            (3, time(23, 30), time(6, 55), 7.1, "Moderate latency after evening training."),
            (2, time(23, 45), time(7, 0), 6.9, "Restless night after heavy caffeine intake."),
            (1, time(23, 15), time(7, 0), 7.6, "Woke feeling refreshed; good sleep latency."),
        ]
        for nights_ago, lights_out, wake_at, duration, note in sleep_nights:
            start_dt = datetime.combine(today - timedelta(days=nights_ago), lights_out)
            end_dt = datetime.combine(today - timedelta(days=nights_ago) + timedelta(days=1), wake_at)
            time_in_bed = (end_dt - start_dt).total_seconds() / 3600.0
            deep = round(duration * 0.22, 1)
            rem = round(duration * 0.24, 1)
            db.add(SleepRecord(
                user_id=user.id,
                sleep_start=start_dt,
                sleep_end=end_dt,
                duration_hours=duration,
                deep_sleep_hours=deep,
                rem_sleep_hours=rem,
                light_sleep_hours=round(duration - deep - rem, 1),
                awake_minutes=int(round((time_in_bed - duration) * 60)),
                efficiency_percentage=round((duration / time_in_bed) * 100.0, 1),
                data_source="SIMULATED_DEMO",
                notes=note
            ))

        # 8. Meals and Hydration - a full week so weekly nutrition metrics are
        #    computed from logged history instead of a single day.
        meal_plan = [
            ("Breakfast", "Steel-cut oatmeal with blueberries, chia seeds, whey protein isolate, and almond butter", time(7, 30), 620, 38.0, 72.0, 18.0),
            ("Lunch", "Grilled chicken breast grain bowl with quinoa, roasted sweet potatoes, and avocado", time(12, 15), 780, 48.0, 85.0, 22.0),
            ("Dinner", "Baked salmon fillet with brown rice, steamed broccoli, and olive-oil dressing", time(19, 15), 710, 44.0, 68.0, 24.0),
        ]
        meals = []
        for day_offset in range(6, -1, -1):
            meal_day = today - timedelta(days=day_offset)
            for meal_type, description, logged_at_time, calories, protein, carbs, fat in meal_plan:
                meals.append(MealLog(
                    user_id=user.id,
                    meal_type=meal_type,
                    description=description,
                    logged_at=datetime.combine(meal_day, logged_at_time),
                    portion_size="Large",
                    calories=calories,
                    protein_g=protein,
                    carbs_g=carbs,
                    fat_g=fat
                ))
        db.add_all(meals)

        hydration_pattern = [(time(7, 45), 500), (time(10, 30), 500), (time(12, 30), 500), (time(14, 15), 550)]
        hydrations = []
        for day_offset in range(6, 0, -1):
            hydration_day = today - timedelta(days=day_offset)
            for logged_at_time, amount in hydration_pattern:
                hydrations.append(HydrationLog(
                    user_id=user.id, amount_ml=amount,
                    logged_at=datetime.combine(hydration_day, logged_at_time)
                ))
        # Today's intake is deliberately still in progress (1850 mL of 2800 mL).
        hydrations.extend([
            HydrationLog(user_id=user.id, amount_ml=500, logged_at=datetime.combine(today, time(7, 45))),
            HydrationLog(user_id=user.id, amount_ml=500, logged_at=datetime.combine(today, time(10, 30))),
            HydrationLog(user_id=user.id, amount_ml=400, logged_at=datetime.combine(today, time(12, 30))),
            HydrationLog(user_id=user.id, amount_ml=450, logged_at=datetime.combine(today, time(14, 15)))
        ])
        db.add_all(hydrations)

        # 9. Past 6 days Daily Load Snapshots for instant trend visualization.
        #    Today's row is written below by the real risk engine so the trend
        #    chart and GET /api/load-risk/current can never disagree.
        for i in range(6):
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

        # 10. Today's Risk Assessment - computed by the real explainable engine
        #     over the rows seeded above, so the stored assessment, today's
        #     snapshot, the dashboard header and Recovery Guide energy mode all
        #     agree instead of showing a hand-written YELLOW 54.2.
        # SessionLocal runs with autoflush=False, so persist everything first:
        # otherwise the engine queries an empty day and stores 0/0/GREEN.
        db.commit()
        risk_predictor.predict_risk(db, user.id)

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
        if owns_session:
            db.close()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="DualWell demo database seeding utility."
    )
    parser.add_argument(
        "--reseed",
        action="store_true",
        help="Delete and regenerate all demo-user data relative to today's date."
    )
    args = parser.parse_args()
    seed_database(reseed=args.reseed)
