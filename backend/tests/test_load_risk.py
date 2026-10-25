from datetime import datetime, timedelta, date
from app.services.load_engine import DualLoadEngine
from app.models.academic import AcademicEvent
from app.models.training import TrainingSession
from app.models.lifestyle import SleepRecord
from app.models.load_risk import DailyLoadSnapshot, RiskAssessment

def test_missing_wearable_metrics_graceful_handling(db, test_user):
    """NFR3: Missing wearable metrics must not crash calculation, adjusts confidence."""
    # User has no wearable metrics or sleep records
    result = DualLoadEngine.calculate_for_user(db, test_user.id)
    assert result is not None
    assert "academic_load_score" in result
    assert "athletic_load_score" in result
    assert "recovery_score" in result
    assert "dual_load_risk_score" in result
    assert result["confidence_score"] <= 60.0  # Missing data lowers confidence

def test_high_academic_and_athletic_load_triggers_risk(db, test_user):
    target_d = date(2026, 10, 20)
    day_mid = datetime(2026, 10, 20, 10, 0, 0)
    
    # Add multiple exams on target day
    e1 = AcademicEvent(
        user_id=test_user.id,
        title="Physics Exam",
        event_type="exam",
        start_time=day_mid,
        end_time=day_mid + timedelta(hours=3),
        priority="critical",
        is_fixed=True
    )
    e2 = AcademicEvent(
        user_id=test_user.id,
        title="Chemistry Lab Exam",
        event_type="exam",
        start_time=day_mid + timedelta(hours=4),
        end_time=day_mid + timedelta(hours=7),
        priority="critical",
        is_fixed=True
    )
    db.add_all([e1, e2])

    # Add high-intensity workout on target day
    t1 = TrainingSession(
        user_id=test_user.id,
        title="HIIT Sprints",
        activity_type="running",
        start_time=day_mid + timedelta(hours=7, minutes=30),
        end_time=day_mid + timedelta(hours=9),
        duration_minutes=90,
        intensity="all_out"
    )
    db.add(t1)

    # Poor sleep record preceding target day (3.5 hours of sleep)
    s1 = SleepRecord(
        user_id=test_user.id,
        sleep_start=datetime(2026, 10, 20, 0, 0, 0),
        sleep_end=datetime(2026, 10, 20, 3, 30, 0),
        duration_hours=3.5,
        data_source="MANUAL_ENTRY"
    )
    db.add(s1)
    db.commit()

    result = DualLoadEngine.calculate_for_user(db, test_user.id, target_date=target_d)
    assert result["academic_load_score"] >= 50.0
    assert result["athletic_load_score"] >= 50.0
    assert result["recovery_score"] <= 60.0
    assert result["dual_load_risk_score"] >= 42.0
    assert result["risk_level"] in ["YELLOW", "RED"]

def test_risk_recalculation_api(client, auth_headers):
    response = client.post("/api/load-risk/recalculate", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "risk_level" in data
    assert "risk_score" in data
    assert "recommended_actions" in data
    assert len(data["recommended_actions"]) > 0

def test_get_current_risk_is_read_only(client, auth_headers, db, test_user):
    """GET /load-risk/current must never persist assessments or daily snapshots.

    The dashboard polls this endpoint on every page load; before this contract
    each poll appended a RiskAssessment row and a DailyLoadSnapshot row.
    """
    assert db.query(RiskAssessment).filter(RiskAssessment.user_id == test_user.id).count() == 0
    assert db.query(DailyLoadSnapshot).filter(DailyLoadSnapshot.user_id == test_user.id).count() == 0

    for _ in range(2):
        response = client.get("/api/load-risk/current", headers=auth_headers)
        assert response.status_code == 200
        assert "risk_level" in response.json()

    assert db.query(RiskAssessment).filter(RiskAssessment.user_id == test_user.id).count() == 0
    assert db.query(DailyLoadSnapshot).filter(DailyLoadSnapshot.user_id == test_user.id).count() == 0

def test_recalculate_upserts_single_snapshot_per_day(client, auth_headers, db, test_user):
    """POST /load-risk/recalculate writes exactly one snapshot row per user per day.

    Repeated recalculations on the same day must update the existing row
    (same id, refreshed values) instead of appending duplicates.
    """
    first = client.post("/api/load-risk/recalculate", headers=auth_headers)
    assert first.status_code == 200

    snapshots = db.query(DailyLoadSnapshot).filter(DailyLoadSnapshot.user_id == test_user.id)
    assert snapshots.count() == 1
    original_id = snapshots.first().id
    assert snapshots.first().snapshot_date == date.today()

    second = client.post("/api/load-risk/recalculate", headers=auth_headers)
    assert second.status_code == 200
    # Old behavior appended a second row for the same day.
    assert snapshots.count() == 1
    assert snapshots.first().id == original_id  # same row updated, not re-inserted

    body = second.json()
    assert body["risk_level"] in ["GREEN", "YELLOW", "RED"]
    assert 0.0 <= body["risk_score"] <= 100.0
