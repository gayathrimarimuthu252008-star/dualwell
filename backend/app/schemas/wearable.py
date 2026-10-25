from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class WearableObservationCreate(BaseModel):
    metric_type: str  # "heart_rate", "hrv", "steps", "resting_hr", "sleep_duration", "recovery_score", "active_minutes"
    value: float
    unit: str
    recorded_at: datetime
    data_source: str = "MANUAL_ENTRY"  # "WEARABLE_LIVE", "SIMULATED_DEMO", "MANUAL_ENTRY"
    extra_metadata: Optional[str] = None

class WearableObservationResponse(BaseModel):
    id: int
    provider: str
    metric_type: str
    value: float
    unit: str
    recorded_at: datetime
    data_source: str
    extra_metadata: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class WearableConnectionResponse(BaseModel):
    id: int
    provider: str
    display_name: str
    is_connected: bool
    last_synced_at: Optional[datetime] = None
    sync_status: str
    error_message: Optional[str] = None

    class Config:
        from_attributes = True

class WearableSyncRequest(BaseModel):
    provider: str = "demo"

class WearableStatusResponse(BaseModel):
    connections: List[WearableConnectionResponse]
    active_provider: Optional[str] = None
    last_sync_time: Optional[datetime] = None
    metrics_summary: Dict[str, Any]
