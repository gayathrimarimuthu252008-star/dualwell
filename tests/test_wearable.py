from datetime import datetime, timedelta
from app.services.wearable.manager import wearable_manager
from app.models.wearable import WearableObservation

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

def test_wearable_providers_documentation(client):
    res = client.get("/api/wearable/providers")
    assert res.status_code == 200
    providers = res.json()
    p_ids = [p["provider_id"] for p in providers]
    assert "demo" in p_ids
    assert "fitbit" in p_ids
    assert "apple_health" in p_ids
    assert "health_connect" in p_ids
