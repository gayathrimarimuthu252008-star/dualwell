from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from app.database import get_db
from app.models.user import User
from app.models.wearable import WearableConnection, WearableObservation
from app.models.lifestyle import SleepRecord
from app.schemas.wearable import (
    WearableObservationCreate, WearableObservationResponse,
    WearableSyncRequest, WearableStatusResponse
)
from app.core.deps import get_current_user
from app.services.wearable.manager import wearable_manager

router = APIRouter(prefix="/wearable", tags=["Wearable Monitoring & Integration"])

@router.get("/status", response_model=WearableStatusResponse)
def get_wearable_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    connections = db.query(WearableConnection).filter(
        WearableConnection.user_id == current_user.id
    ).all()

    # If no connections exist yet, seed the default demo connection entry
    if not connections:
        default_conn = WearableConnection(
            user_id=current_user.id,
            provider="demo",
            display_name="DualWell Athlete Simulator (Demo Engine)",
            is_connected=True,
            sync_status="idle"
        )
        db.add(default_conn)
        db.commit()
        db.refresh(default_conn)
        connections = [default_conn]

    # Metrics summary for quick card glance
    recent_hr = db.query(WearableObservation).filter(
        WearableObservation.user_id == current_user.id,
        WearableObservation.metric_type == "heart_rate"
    ).order_by(WearableObservation.recorded_at.desc()).first()

    recent_hrv = db.query(WearableObservation).filter(
        WearableObservation.user_id == current_user.id,
        WearableObservation.metric_type == "hrv"
    ).order_by(WearableObservation.recorded_at.desc()).first()

    recent_steps = db.query(WearableObservation).filter(
        WearableObservation.user_id == current_user.id,
        WearableObservation.metric_type == "steps"
    ).order_by(WearableObservation.recorded_at.desc()).first()

    recent_resting = db.query(WearableObservation).filter(
        WearableObservation.user_id == current_user.id,
        WearableObservation.metric_type == "resting_hr"
    ).order_by(WearableObservation.recorded_at.desc()).first()

    # Average sleep is computed from real logged sleep records (last 7 days).
    # Missing metrics return null instead of invented fallback numbers.
    avg_sleep_row = db.query(func.avg(SleepRecord.duration_hours)).filter(
        SleepRecord.user_id == current_user.id,
        SleepRecord.sleep_end >= datetime.utcnow() - timedelta(days=7)
    ).scalar()

    last_sync = max([c.last_synced_at for c in connections if c.last_synced_at], default=None)
    active_conn = next((c.provider for c in connections if c.is_connected), "demo")

    return {
        "connections": connections,
        "active_provider": active_conn,
        "last_sync_time": last_sync,
        "metrics_summary": {
            "heart_rate": recent_hr.value if recent_hr else None,
            "hrv": recent_hrv.value if recent_hrv else None,
            "steps": int(recent_steps.value) if recent_steps else None,
            "resting_hr": recent_resting.value if recent_resting else None,
            "sleep_hours": round(float(avg_sleep_row), 1) if avg_sleep_row is not None else None,
            "source": recent_hr.data_source if recent_hr else None
        }
    }

@router.get("/providers")
def list_providers():
    """Lists supported wearable provider adapters and their technical documentation."""
    return wearable_manager.list_available_providers()

@router.post("/connect/{provider_id}")
def connect_provider(
    provider_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    provider = wearable_manager.get_provider(provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Wearable provider not recognized.")

    if provider.availability == "coming_soon":
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=f"{provider.display_name} integration is coming soon and cannot be connected yet."
        )

    conn = db.query(WearableConnection).filter(
        WearableConnection.user_id == current_user.id,
        WearableConnection.provider == provider_id
    ).first()

    if not conn:
        conn = WearableConnection(
            user_id=current_user.id,
            provider=provider_id,
            display_name=provider.display_name,
            is_connected=True,
            sync_status="idle"
        )
        db.add(conn)
    else:
        conn.is_connected = True
        conn.sync_status = "idle"
        conn.error_message = None

    db.commit()
    return {"message": f"Connected to {provider.display_name} successfully.", "provider": provider_id}

@router.post("/disconnect/{provider_id}")
def disconnect_provider(
    provider_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conn = db.query(WearableConnection).filter(
        WearableConnection.user_id == current_user.id,
        WearableConnection.provider == provider_id
    ).first()

    if conn:
        conn.is_connected = False
        conn.sync_status = "idle"
        db.commit()

    return {"message": f"Disconnected {provider_id}."}

@router.post("/sync")
def sync_wearable(
    sync_req: WearableSyncRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        result = wearable_manager.sync_provider(db, current_user.id, sync_req.provider)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Synchronization failed: {str(e)}"
        )

@router.get("/observations", response_model=List[WearableObservationResponse])
def get_observations(
    metric_type: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(WearableObservation).filter(WearableObservation.user_id == current_user.id)
    if metric_type:
        query = query.filter(WearableObservation.metric_type == metric_type)
    
    return query.order_by(WearableObservation.recorded_at.desc()).limit(limit).all()

@router.post("/observations", response_model=WearableObservationResponse)
def add_observation(
    obs_in: WearableObservationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    obs = WearableObservation(
        user_id=current_user.id,
        provider="manual",
        metric_type=obs_in.metric_type,
        value=obs_in.value,
        unit=obs_in.unit,
        recorded_at=obs_in.recorded_at,
        data_source=obs_in.data_source,
        extra_metadata=obs_in.extra_metadata
    )
    db.add(obs)
    db.commit()
    db.refresh(obs)
    return obs
