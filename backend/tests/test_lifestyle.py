from datetime import datetime, timedelta

def test_meal_logging(client, auth_headers):
    res = client.post("/api/lifestyle/meals", headers=auth_headers, json={
        "meal_type": "Lunch",
        "description": "Quinoa bowl with salmon and avocado",
        "calories": 650,
        "protein_g": 42.0,
        "carbs_g": 60.0,
        "fat_g": 22.0
    })
    assert res.status_code == 201
    assert res.json()["description"] == "Quinoa bowl with salmon and avocado"

def test_hydration_logging_and_quick_add(client, auth_headers):
    # Quick add 250ml
    res = client.post("/api/lifestyle/hydration/quick-add", headers=auth_headers, json={
        "amount_ml": 250
    })
    assert res.status_code == 200
    data = res.json()
    assert data["total_consumed_ml"] >= 250
    assert "smart_tip" in data

def test_sleep_and_personalized_planner(client, auth_headers):
    now = datetime.utcnow()
    # Log sleep
    res1 = client.post("/api/lifestyle/sleep", headers=auth_headers, json={
        "sleep_start": (now - timedelta(hours=9)).isoformat(),
        "sleep_end": (now - timedelta(hours=1)).isoformat(),
        "duration_hours": 8.0,
        "deep_sleep_hours": 2.0,
        "rem_sleep_hours": 2.0,
        "light_sleep_hours": 4.0,
        "data_source": "MANUAL_ENTRY"
    })
    assert res1.status_code == 200

    # Get sleep plan
    res2 = client.get("/api/lifestyle/sleep-plan", headers=auth_headers)
    assert res2.status_code == 200
    plan = res2.json()
    assert "target_bedtime" in plan
    assert "recommended_winddown_time" in plan
    assert "advice" in plan

def test_sleep_plan_reports_real_average_or_null(client, auth_headers):
    """sleep-plan must average real sleep records, or return null.

    The old endpoint always returned the hardcoded value 7.4 regardless of
    what the student had actually logged.
    """
    now = datetime.utcnow()

    # No records -> null instead of a made-up average.
    res = client.get("/api/lifestyle/sleep-plan", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["actual_average_hours"] is None

    # Two real records -> their average.
    for hours in (6.5, 7.5):
        client.post("/api/lifestyle/sleep", headers=auth_headers, json={
            "sleep_start": (now - timedelta(hours=hours + 1)).isoformat(),
            "sleep_end": (now - timedelta(hours=1)).isoformat(),
            "duration_hours": hours,
            "data_source": "MANUAL_ENTRY"
        })

    res2 = client.get("/api/lifestyle/sleep-plan", headers=auth_headers)
    assert res2.status_code == 200
    assert res2.json()["actual_average_hours"] == 7.0

def test_recovery_checkin(client, auth_headers):
    res = client.post("/api/lifestyle/recovery-checkin", headers=auth_headers, json={
        "muscle_soreness": 4,
        "mental_fatigue": 5,
        "sleep_readiness": 7,
        "has_pain_or_strain": False
    })
    assert res.status_code == 200
    data = res.json()
    assert data["muscle_soreness"] == 4
