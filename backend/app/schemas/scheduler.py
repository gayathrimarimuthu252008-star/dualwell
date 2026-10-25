from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ScheduleRecommendationResponse(BaseModel):
    id: int
    related_event_id: Optional[int] = None
    event_title: str
    event_category: str
    original_start_time: Optional[datetime] = None
    original_end_time: Optional[datetime] = None
    proposed_start_time: datetime
    proposed_end_time: datetime
    action_type: str
    rationale: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class RecommendationActionRequest(BaseModel):
    recommendation_id: int
    action: str  # "accept", "reject"

class DynamicSchedulePlanResponse(BaseModel):
    pending_recommendations: List[ScheduleRecommendationResponse]
    conflicts_resolved: int
    recovery_windows_added: int
    protected_sleep_hours: float
    summary: str
