def test_privacy_settings_update(client, auth_headers):
    res = client.put("/api/privacy/settings", headers=auth_headers, json={
        "consent_wearable_sync": True,
        "allow_overload_notifications": False,
        "quiet_hours_enabled": True,
        "quiet_hours_start": "23:00",
        "quiet_hours_end": "07:00"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["allow_overload_notifications"] is False
    assert data["quiet_hours_start"] == "23:00"

def test_student_data_export(client, auth_headers):
    res = client.get("/api/privacy/export-data", headers=auth_headers)
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/json"
    data = res.json()
    assert "export_metadata" in data
    assert "academic_events" in data
    assert "training_sessions" in data
    assert "wearable_telemetry_summary" in data

def test_student_data_isolation(client):
    # Register Student A
    res_a = client.post("/api/auth/register", json={
        "email": "student.a@dualwell.edu",
        "password": "Password123!",
        "full_name": "Student A"
    })
    token_a = res_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Register Student B
    res_b = client.post("/api/auth/register", json={
        "email": "student.b@dualwell.edu",
        "password": "Password123!",
        "full_name": "Student B"
    })
    token_b = res_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Student A logs a private event
    client.post("/api/academic/events", headers=headers_a, json={
        "title": "Confidential Honors Thesis Defense",
        "event_type": "exam",
        "start_time": "2026-11-01T10:00:00",
        "end_time": "2026-11-01T12:00:00"
    })

    # Student B queries events - must NOT see Student A's events
    events_b = client.get("/api/academic/events", headers=headers_b).json()
    titles_b = [e["title"] for e in events_b]
    assert "Confidential Honors Thesis Defense" not in titles_b

def test_weekly_insights(client, auth_headers):
    res = client.get("/api/insights/weekly", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "week_range" in data
    assert "daily_trends" in data
    assert len(data["daily_trends"]) == 7
    assert "risk_distribution" in data
    assert "key_recommendations" in data
