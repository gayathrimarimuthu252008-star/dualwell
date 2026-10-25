from datetime import datetime, timedelta
from app.models.academic import AcademicEvent
from app.models.training import TrainingSession
from app.services.scheduler_engine import DynamicSchedulerEngine

def test_calendar_conflicts_detection(client, auth_headers):
    now = datetime.utcnow()
    # Create conflicting academic and training sessions
    client.post("/api/academic/events", headers=auth_headers, json={
        "title": "Algorithms Lecture",
        "event_type": "class",
        "start_time": (now + timedelta(hours=3)).isoformat(),
        "end_time": (now + timedelta(hours=5)).isoformat(),
        "is_fixed": True
    })

    client.post("/api/training/sessions", headers=auth_headers, json={
        "title": "Gym Lifting",
        "activity_type": "strength",
        "start_time": (now + timedelta(hours=4)).isoformat(),
        "end_time": (now + timedelta(hours=5, minutes=30)).isoformat(),
        "is_flexible": True
    })

    res = client.get("/api/academic/conflicts", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["has_conflicts"] is True
    assert data["conflict_count"] >= 1

def test_dynamic_scheduler_recommendations_and_apply(db, test_user):
    now = datetime.utcnow()
    # Fixed event
    e = AcademicEvent(
        user_id=test_user.id,
        title="Mandatory Exam",
        event_type="exam",
        start_time=now + timedelta(hours=2),
        end_time=now + timedelta(hours=4),
        is_fixed=True
    )
    # Flexible training overlapping
    t = TrainingSession(
        user_id=test_user.id,
        title="Rowing Erg Practice",
        activity_type="rowing",
        start_time=now + timedelta(hours=3),
        end_time=now + timedelta(hours=4, minutes=30),
        duration_minutes=90,
        is_flexible=True
    )
    db.add_all([e, t])
    db.commit()

    recs = DynamicSchedulerEngine.generate_recommendations(db, test_user.id)
    assert len(recs) >= 1
    rec = recs[0]
    assert rec.status == "pending"
    assert rec.action_type == "SHIFT_TIME"

    # Apply recommendation
    success = DynamicSchedulerEngine.apply_recommendation(db, test_user.id, rec.id)
    assert success is True
    assert rec.status == "accepted"
