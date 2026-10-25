from datetime import datetime, timedelta
import app.services.wearable.demo_provider as demo_provider_module
from app.services.wearable.manager import wearable_manager
from app.models.wearable import WearableObservation
from app.models.lifestyle import SleepRecord

def test_wearable_status_endpoint(client, auth_headers):
    res = client.get("/api/wearable/status", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "connections" in data
    assert "metrics_summary" in data

def test_wearable_demo_sync_and_duplicate_prevention(db, test_user):
    # First sync
    res1 = wearable_manager.sync_provider(db, test_user.id, "demo")
    assert res1["status"] == "success"
    assert res1["observations_ingested"] > 0
    count_after_first = db.query(WearableObservation).filter(WearableObservation.user_id == test_user.id).count()

    # Immediate second sync with same timestamps
    res2 = wearable_manager.sync_provider(db, test_user.id, "demo")
    assert res2["status"] == "success"
    # Duplicate prevention should prevent explosion of records
    count_after_second = db.query(WearableObservation).filter(WearableObservation.user_id == test_user.id).count()
    assert count_after_second == count_after_first

def test_demo_sync_timestamps_stable_across_clock_drift(db, test_user, monkeypatch):
    """Demo observations must use stable timestamps so the unique constraint dedupes.

    The wall clock is advanced 12 minutes between two syncs. That crosses the
    old 5-minute bucket boundary, which used to shift every recorded_at and
    insert a full duplicate set of observations.
    """
    class FrozenClock(datetime):
        current = None

        @classmethod
        def utcnow(cls):
            return cls.current

    FrozenClock.current = datetime(2026, 10, 16, 10, 0, 0)
    monkeypatch.setattr(demo_provider_module, "datetime", FrozenClock)

    first = wearable_manager.sync_provider(db, test_user.id, "demo")
    assert first["status"] == "success"
    assert first["observations_ingested"] > 0
    count_after_first = db.query(WearableObservation).filter(
        WearableObservation.user_id == test_user.id
    ).count()

    # Cross the old 5-minute bucket boundary.
    FrozenClock.current = datetime(2026, 10, 16, 10, 12, 0)
    second = wearable_manager.sync_provider(db, test_user.id, "demo")
    assert second["status"] == "success"
    count_after_second = db.query(WearableObservation).filter(
        WearableObservation.user_id == test_user.id
    ).count()

    # Old behavior: every recorded_at moved, so nothing was recognized as duplicate.
    assert second["observations_ingested"] == 0
    assert second["duplicates_prevented"] > 0
    assert count_after_second == count_after_first

def test_wearable_status_returns_null_without_invented_fallbacks(client, auth_headers, db, test_user):
    """Status metrics must be null when no data exists -- never made-up numbers.

    The old endpoint returned 68.0 bpm / 62.0 ms / 9420 steps / 7.5 h
    fallbacks, and sleep_hours was the single latest observation rather than
    an average of real sleep records.
    """
    res = client.get("/api/wearable/status", headers=auth_headers)
    assert res.status_code == 200
    metrics = res.json()["metrics_summary"]
    assert metrics["heart_rate"] is None
    assert metrics["hrv"] is None
    assert metrics["steps"] is None
    assert metrics["resting_hr"] is None
    assert metrics["sleep_hours"] is None
    assert metrics["source"] is None

    # With two real sleep records, sleep_hours becomes their average.
    now = datetime.utcnow()
    for i, hours in enumerate([6.0, 8.0]):
        db.add(SleepRecord(
            user_id=test_user.id,
            sleep_start=now - timedelta(hours=hours + 1),
            sleep_end=now - timedelta(hours=1 + i),
            duration_hours=hours,
            data_source="MANUAL_ENTRY"
        ))
    db.commit()

    res2 = client.get("/api/wearable/status", headers=auth_headers)
    assert res2.status_code == 200
    assert res2.json()["metrics_summary"]["sleep_hours"] == 7.0

def test_wearable_providers_documentation(client):
    res = client.get("/api/wearable/providers")
    assert res.status_code == 200
    providers = res.json()
    p_ids = [p["provider_id"] for p in providers]
    assert "demo" in p_ids
    assert "fitbit" in p_ids
    assert "apple_health" in p_ids
    assert "health_connect" in p_ids
