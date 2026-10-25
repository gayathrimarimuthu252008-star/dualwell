from datetime import datetime, timedelta


def test_notification_center_generates_smart_reminders(client, auth_headers):
    res = client.get("/api/notifications/reminders", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()

    assert isinstance(data["unread_count"], int)
    assert isinstance(data["quiet_hours_active"], bool)

    reminders = data["reminders"]
    # Hydration + wind-down prompts are always generated for an empty center.
    assert len(reminders) >= 2
    categories = {r["category"] for r in reminders}
    assert "HYDRATION" in categories
    assert "SLEEP_PREP" in categories

    unread = sum(1 for r in reminders if not r["is_read"])
    assert data["unread_count"] == unread


def test_mark_reminder_read(client, auth_headers):
    reminders = client.get("/api/notifications/reminders", headers=auth_headers).json()["reminders"]
    target = reminders[0]

    res = client.post(f"/api/notifications/reminders/{target['id']}/read", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["is_read"] is True

    center = client.get("/api/notifications/reminders", headers=auth_headers).json()
    assert all(r["is_read"] for r in center["reminders"] if r["id"] == target["id"])
    # Unread count must stay consistent with the reminder list.
    assert center["unread_count"] == sum(1 for r in center["reminders"] if not r["is_read"])


def test_dismiss_reminder_removes_it_from_center(client, auth_headers):
    reminders = client.get("/api/notifications/reminders", headers=auth_headers).json()["reminders"]
    target = reminders[0]

    res = client.post(f"/api/notifications/reminders/{target['id']}/dismiss", headers=auth_headers)
    assert res.status_code == 200

    center = client.get("/api/notifications/reminders", headers=auth_headers).json()
    assert target["id"] not in [r["id"] for r in center["reminders"]]


def test_unknown_reminder_returns_404(client, auth_headers):
    assert client.post("/api/notifications/reminders/999999/read", headers=auth_headers).status_code == 404
    assert client.post("/api/notifications/reminders/999999/dismiss", headers=auth_headers).status_code == 404


def test_quiet_hours_active_flag(client, auth_headers):
    # Window computed from "now" so the flag is deterministically active:
    # start = current minute, end = one minute earlier (crosses midnight).
    now = datetime.utcnow().replace(second=0, microsecond=0)
    end = now - timedelta(minutes=1)

    res = client.put("/api/privacy/settings", headers=auth_headers, json={
        "quiet_hours_enabled": True,
        "quiet_hours_start": now.strftime("%H:%M"),
        "quiet_hours_end": end.strftime("%H:%M"),
    })
    assert res.status_code == 200

    center = client.get("/api/notifications/reminders", headers=auth_headers)
    assert center.status_code == 200
    assert center.json()["quiet_hours_active"] is True
