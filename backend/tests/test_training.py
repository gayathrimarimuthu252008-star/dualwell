from datetime import datetime, timedelta


def _session_payload(**overrides):
    start = datetime.utcnow().replace(microsecond=0) + timedelta(days=1)
    payload = {
        "title": "Threshold Intervals",
        "activity_type": "running",
        "start_time": start.isoformat(),
        "end_time": (start + timedelta(minutes=45)).isoformat(),
        "duration_minutes": 45,
        "intensity": "high",
        "perceived_exertion": 8,
    }
    payload.update(overrides)
    return payload


def test_create_and_list_training_sessions(client, auth_headers):
    res = client.post("/api/training/sessions", headers=auth_headers, json=_session_payload())
    assert res.status_code == 201
    created = res.json()
    assert created["title"] == "Threshold Intervals"
    assert created["activity_type"] == "running"
    assert created["user_id"] is not None

    listed = client.get("/api/training/sessions", headers=auth_headers)
    assert listed.status_code == 200
    assert created["id"] in [s["id"] for s in listed.json()]


def test_training_session_requires_end_after_start(client, auth_headers):
    start = datetime.utcnow()
    res = client.post("/api/training/sessions", headers=auth_headers, json=_session_payload(
        start_time=start.isoformat(),
        end_time=(start - timedelta(minutes=30)).isoformat(),
    ))
    assert res.status_code == 400
    assert "after start" in res.json()["detail"]


def test_update_training_session(client, auth_headers):
    created = client.post("/api/training/sessions", headers=auth_headers, json=_session_payload()).json()

    res = client.put(f"/api/training/sessions/{created['id']}", headers=auth_headers, json={
        "title": "Recovery Spin",
        "intensity": "light",
    })
    assert res.status_code == 200
    updated = res.json()
    assert updated["title"] == "Recovery Spin"
    assert updated["intensity"] == "light"
    # Fields omitted from the payload must be preserved (model_dump exclude_unset).
    assert updated["activity_type"] == created["activity_type"]
    assert updated["duration_minutes"] == created["duration_minutes"]


def test_delete_training_session(client, auth_headers):
    created = client.post("/api/training/sessions", headers=auth_headers, json=_session_payload()).json()
    sid = created["id"]

    res = client.delete(f"/api/training/sessions/{sid}", headers=auth_headers)
    assert res.status_code == 204

    remaining = client.get("/api/training/sessions", headers=auth_headers).json()
    assert sid not in [s["id"] for s in remaining]

    assert client.delete(f"/api/training/sessions/{sid}", headers=auth_headers).status_code == 404


def test_training_sessions_are_isolated_between_users(client):
    res_a = client.post("/api/auth/register", json={
        "email": "train.a@dualwell.edu",
        "password": "Password123!",
        "full_name": "Train A",
    })
    headers_a = {"Authorization": f"Bearer {res_a.json()['access_token']}"}
    res_b = client.post("/api/auth/register", json={
        "email": "train.b@dualwell.edu",
        "password": "Password123!",
        "full_name": "Train B",
    })
    headers_b = {"Authorization": f"Bearer {res_b.json()['access_token']}"}

    created = client.post("/api/training/sessions", headers=headers_a, json=_session_payload()).json()

    # Student B must neither see nor delete Student A's session.
    listed_b = client.get("/api/training/sessions", headers=headers_b).json()
    assert created["id"] not in [s["id"] for s in listed_b]
    assert client.delete(
        f"/api/training/sessions/{created['id']}", headers=headers_b
    ).status_code == 404
