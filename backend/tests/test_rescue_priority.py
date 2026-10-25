from datetime import datetime, timedelta
from app.models.academic import AcademicEvent


def _add_event(db, user_id, title, priority, start_time):
    db.add(AcademicEvent(
        user_id=user_id,
        title=title,
        event_type="deadline",
        start_time=start_time,
        end_time=start_time + timedelta(hours=1),
        priority=priority,
        is_fixed=True,
        is_completed=False,
    ))


def test_rescue_plan_orders_events_by_priority_rank(client, auth_headers, db, test_user):
    """Rescue triage must sort critical > high > medium > low.

    The old query ordered by ``priority.desc()`` on a plain string column, so
    SQLite returned alphabetically descending: medium, low, high, critical --
    putting a medium-priority item in DO NOW and the critical item in POSTPONE.
    Lower-priority events are deliberately given the *earlier* start times here
    so only the priority rank can put the critical event first.
    """
    now = datetime.utcnow()
    _add_event(db, test_user.id, "Low Priority Warmup Drill", "low", now + timedelta(hours=1))
    _add_event(db, test_user.id, "Medium Priority Reading", "medium", now + timedelta(hours=2))
    _add_event(db, test_user.id, "High Priority Lab Report", "high", now + timedelta(hours=3))
    _add_event(db, test_user.id, "Critical Priority Final Exam", "critical", now + timedelta(hours=5))
    db.commit()

    response = client.get("/api/rescue/plan", headers=auth_headers)
    assert response.status_code == 200
    items = response.json()["action_items"]

    assert items[0]["urgency_tier"] == "NOW"
    assert "Critical Priority Final Exam" in items[0]["title"]

    assert items[1]["urgency_tier"] == "NEXT"
    assert "High Priority Lab Report" in items[1]["title"]

    postponed = [i["title"] for i in items if i["urgency_tier"] == "POSTPONE"]
    assert postponed == [
        "Defer Medium Priority Reading",
        "Defer Low Priority Warmup Drill",
    ]


def test_rescue_plan_response_shape(client, auth_headers):
    """Every plan must satisfy the RescuePlanResponse contract."""
    response = client.get("/api/rescue/plan", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()

    for key in (
        "is_active", "summary_headline", "estimated_energy_level",
        "action_items", "training_adjustment", "hydration_nutrition_alert",
        "generated_at",
    ):
        assert key in data

    assert isinstance(data["action_items"], list)
    for item in data["action_items"]:
        for field in (
            "id", "order", "title", "urgency_tier", "category",
            "duration_minutes", "reason", "is_completed",
        ):
            assert field in item
        assert item["urgency_tier"] in ("NOW", "NEXT", "POSTPONE")
        assert item["is_completed"] is False


def test_rescue_regenerate_returns_fresh_plan(client, auth_headers):
    first = client.get("/api/rescue/plan", headers=auth_headers)
    assert first.status_code == 200

    regen = client.post("/api/rescue/regenerate", headers=auth_headers)
    assert regen.status_code == 200
    data = regen.json()

    # Same contract as GET, with a fresh generation timestamp.
    assert set(data.keys()) == set(first.json().keys())
    assert data["generated_at"]
