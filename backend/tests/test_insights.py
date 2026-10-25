from datetime import datetime, date, time, timedelta

from app.models.lifestyle import HydrationLog, MealLog, SleepRecord


def test_weekly_insights_response_shape(client, auth_headers):
    res = client.get("/api/insights/weekly", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()

    for key in (
        "week_range", "academic_workload_trend", "training_duration_trend",
        "sleep_consistency_score", "hydration_logging_consistency",
        "meal_logging_consistency", "risk_distribution", "recovery_trend_summary",
        "completed_vs_missed_tasks", "daily_trends", "key_recommendations",
    ):
        assert key in data

    # Exactly one trend point per day of the reporting window.
    assert len(data["daily_trends"]) == 7
    for point in data["daily_trends"]:
        for field in (
            "day", "date", "academic_load", "athletic_load",
            "recovery_score", "dual_risk", "sleep_hours", "hydration_ml",
        ):
            assert field in point

    dist = data["risk_distribution"]
    assert set(dist.keys()) == {"green_days", "yellow_days", "red_days"}
    assert all(isinstance(v, int) for v in dist.values())

    assert isinstance(data["completed_vs_missed_tasks"], dict)
    assert isinstance(data["key_recommendations"], list)


def test_weekly_insights_with_logged_activity(client, auth_headers):
    start = datetime.utcnow() - timedelta(days=1)
    created = client.post("/api/training/sessions", headers=auth_headers, json={
        "title": "Tempo Run",
        "activity_type": "running",
        "start_time": start.isoformat(),
        "end_time": (start + timedelta(hours=1)).isoformat(),
        "duration_minutes": 60,
        "intensity": "high",
    })
    assert created.status_code == 201

    res = client.get("/api/insights/weekly", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert len(data["daily_trends"]) == 7
    assert isinstance(data["training_duration_trend"], str)
    assert isinstance(data["week_range"], str)


def test_weekly_insights_reports_zeros_for_empty_week(client, auth_headers):
    """An empty week must be all zeros -- never invented numbers.

    Guards the Phase 3.2 fixes in ``insights_engine.py``:
      * meal consistency returned 80.0 when nothing was logged (and 9.5%
        for the seeded demo via the meals/21 formula),
      * hydration counted a hard-coded 2200 mL/day as meeting the 2L target,
      * missing sleep fell back to a hard-coded 7.5 h,
      * days without a snapshot plotted a synthetic ramp 55 + (i*3) % 20.
    """
    res = client.get("/api/insights/weekly", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()

    assert data["meal_logging_consistency"] == 0.0
    assert data["hydration_logging_consistency"] == 0.0
    assert data["sleep_consistency_score"] == 0.0

    for point in data["daily_trends"]:
        assert point["academic_load"] == 0.0
        assert point["athletic_load"] == 0.0
        assert point["dual_risk"] == 0.0
        assert point["recovery_score"] == 0.0
        assert point["sleep_hours"] == 0.0
        assert point["hydration_ml"] == 0

    # No snapshot -> no ramp: the old synthetic trend produced YELLOW/RED days.
    assert data["risk_distribution"] == {
        "green_days": 7, "yellow_days": 0, "red_days": 0,
    }


def test_weekly_insights_metrics_derived_only_from_real_logs(db, client, auth_headers, test_user):
    """Consistency scores must be computed from actual logs only (Phase 3.2).

    * meal        = days with >= 1 meal / 7       -> 3 days  = 42.9
                    (old meals/21 formula would give 14.3)
    * hydration   = days >= 2000 mL / 7           -> 2 days  = 28.6
                    (old hard-coded 2200 mL would give 100.0)
    * sleep score = avg(real sleep) / 8h * 92     -> 26.3
                    (old 7.5 h fallback would give 86.3)
    """
    today = date.today()

    # Meals on exactly 3 distinct days inside the reporting window.
    for days_ago in (3, 2, 1):
        db.add(MealLog(
            user_id=test_user.id, meal_type="Lunch", description="Test meal",
            logged_at=datetime.combine(today - timedelta(days=days_ago), time(12, 0)),
            portion_size="Medium", calories=600, protein_g=30.0,
            carbs_g=60.0, fat_g=20.0,
        ))

    # >= 2000 mL on exactly 2 days; one day stays under the target.
    db.add(HydrationLog(user_id=test_user.id, amount_ml=2100,
                        logged_at=datetime.combine(today - timedelta(days=4), time(10, 0))))
    db.add(HydrationLog(user_id=test_user.id, amount_ml=2000,
                        logged_at=datetime.combine(today - timedelta(days=2), time(10, 0))))
    db.add(HydrationLog(user_id=test_user.id, amount_ml=1500,
                        logged_at=datetime.combine(today - timedelta(days=1), time(10, 0))))

    # Two nights of exactly 8 h, each contained in a single calendar day.
    for days_ago in (3, 2):
        d = today - timedelta(days=days_ago)
        db.add(SleepRecord(
            user_id=test_user.id,
            sleep_start=datetime.combine(d, time(1, 0)),
            sleep_end=datetime.combine(d, time(9, 0)),
            duration_hours=8.0, data_source="MANUAL_ENTRY",
        ))
    db.commit()

    res = client.get("/api/insights/weekly", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()

    assert data["meal_logging_consistency"] == 42.9        # 3 / 7
    assert data["hydration_logging_consistency"] == 28.6   # 2 / 7
    assert data["sleep_consistency_score"] == 26.3         # (16/7) / 8 * 92

    # Per-day sleep reads the real logs: two 8.0 h days, five empty days.
    sleeps = sorted(p["sleep_hours"] for p in data["daily_trends"])
    assert sleeps == [0.0, 0.0, 0.0, 0.0, 0.0, 8.0, 8.0]

    # Per-day hydration reads the real logs too (no 2200 mL phantom days).
    waters = sorted(p["hydration_ml"] for p in data["daily_trends"])
    assert waters == [0, 0, 0, 0, 1500, 2000, 2100]
