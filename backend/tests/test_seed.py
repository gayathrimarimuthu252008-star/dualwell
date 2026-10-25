from datetime import date, datetime, timedelta
from app.seed import DEMO_EMAIL, seed_database
from app.models.user import User
from app.models.academic import AcademicEvent
from app.models.lifestyle import MealLog
from app.models.load_risk import DailyLoadSnapshot, RiskAssessment
from app.services.insights_engine import WeeklyInsightsEngine
from app.services.risk_prediction import risk_predictor


def test_reseed_regenerates_demo_data_relative_to_today(db):
    """`seed_database(reseed=True)` must wipe and rebuild the demo persona.

    The old seeder returned early whenever the demo user existed, so stale
    data (e.g. events seeded on a previous day) could never be refreshed.
    """
    # Seed once against an empty test database.
    seed_database(db=db)
    user = db.query(User).filter(User.email == "alex.morgan@dualwell.edu").first()
    assert user is not None

    exam = db.query(AcademicEvent).filter_by(
        user_id=user.id, title="Advanced Algorithms Final Exam"
    ).first()
    assert exam is not None
    assert exam.start_time.date() == date.today() + timedelta(days=2)

    # Pollute with a stale leftover, simulating data generated on another day.
    db.add(AcademicEvent(
        user_id=user.id,
        title="Stale leftover event",
        event_type="assignment",
        start_time=datetime(2020, 1, 1, 9, 0),
        end_time=datetime(2020, 1, 1, 10, 0),
        priority="low"
    ))
    db.commit()

    # Reseed: the demo user and all their records are rebuilt relative to today.
    seed_database(reseed=True, db=db)
    db.expire_all()

    users = db.query(User).filter(User.email == "alex.morgan@dualwell.edu").all()
    assert len(users) == 1
    user = users[0]

    assert db.query(AcademicEvent).filter_by(
        user_id=user.id, title="Stale leftover event"
    ).count() == 0

    exam = db.query(AcademicEvent).filter_by(
        user_id=user.id, title="Advanced Algorithms Final Exam"
    ).first()
    assert exam is not None
    assert exam.start_time.date() == date.today() + timedelta(days=2)


def test_seed_is_idempotent_across_repeated_startups(db):
    """create_all + seed_database run on every boot; they must not duplicate.

    The lifespan calls them on each startup (and gunicorn may boot several
    workers), so a second run has to be a no-op: the demo user already
    exists -> skip, and every seeded table keeps its exact row count. The
    unique email constraint is the backstop for the concurrent-worker race.
    """
    seed_database(db=db)

    demo_id = db.query(User).filter_by(email=DEMO_EMAIL).one().id

    def counts():
        db.expire_all()
        return {
            "users": db.query(User).filter_by(email=DEMO_EMAIL).count(),
            "events": db.query(AcademicEvent).filter_by(user_id=demo_id).count(),
            "meals": db.query(MealLog).filter_by(user_id=demo_id).count(),
        }

    before = counts()
    assert before["users"] == 1

    # Second and third "startup" against the same database.
    seed_database(db=db)
    seed_database(db=db)
    after = counts()

    assert after == before
    assert db.query(User).filter_by(email=DEMO_EMAIL).count() == 1


def test_seeded_todays_snapshot_matches_live_engine(db):
    """Today's stored snapshot, assessment and insights row must come from the
    real engine and agree with a live recomputation.

    Guards the Phase 3.3 fixes:
      * the seeder used to write a hand-made YELLOW 57.2 (assessment 54.2)
        while GET /load-risk/current computed RED 70.9, so the dashboard
        header, Weekly Insights and Rescue Mode all disagreed;
      * SessionLocal's autoflush=False meant a missing commit let the engine
        evaluate an empty day and persist 0/0/GREEN.
    """
    seed_database(db=db)
    demo = db.query(User).filter_by(email=DEMO_EMAIL).one()
    today = date.today()

    # Exactly one snapshot row for today (upsert target, no duplicates).
    today_rows = db.query(DailyLoadSnapshot).filter_by(
        user_id=demo.id, snapshot_date=today
    ).all()
    assert len(today_rows) == 1
    snap = today_rows[0]

    # Not the empty-day signature the missing-commit bug produced.
    assert snap.academic_load_score > 0
    assert snap.athletic_load_score > 0
    assert snap.dual_load_risk_score > 0

    # A live, read-only recomputation over the same rows must match exactly.
    live = risk_predictor.compute_risk(db, demo.id)
    assert snap.risk_level == live["risk_level"]
    assert snap.dual_load_risk_score == live["risk_score"]
    assert snap.academic_load_score == live["academic_component"]
    assert snap.athletic_load_score == live["athletic_component"]
    assert snap.recovery_score == live["recovery_component"]

    # The stored assessment that drives Rescue Mode's energy level agrees.
    assessment = db.query(RiskAssessment).filter_by(
        user_id=demo.id
    ).order_by(RiskAssessment.calculated_at.desc()).first()
    assert assessment is not None
    assert assessment.risk_level == snap.risk_level
    assert assessment.risk_score == snap.dual_load_risk_score

    # The weekly-insights trend row for today shows the same numbers.
    report = WeeklyInsightsEngine.generate_weekly_report(db, demo.id)
    today_point = report.daily_trends[-1]
    assert today_point.academic_load == round(snap.academic_load_score, 1)
    assert today_point.athletic_load == round(snap.athletic_load_score, 1)
    assert today_point.dual_risk == round(snap.dual_load_risk_score, 1)
