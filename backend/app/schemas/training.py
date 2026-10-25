from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TrainingSessionBase(BaseModel):
    title: str
    activity_type: str  # "running", "rowing", "strength", "hiit", "cycling", "mobility", "swimming"
    start_time: datetime
    end_time: datetime
    duration_minutes: int = 60
    intensity: str = "moderate"  # "light", "moderate", "high", "all_out"
    avg_heart_rate: Optional[float] = None
    max_heart_rate: Optional[float] = None
    perceived_exertion: Optional[int] = None  # 1-10
    is_flexible: bool = True
    notes: Optional[str] = None

class TrainingSessionCreate(TrainingSessionBase):
    pass

class TrainingSessionUpdate(BaseModel):
    title: Optional[str] = None
    activity_type: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    intensity: Optional[str] = None
    avg_heart_rate: Optional[float] = None
    max_heart_rate: Optional[float] = None
    perceived_exertion: Optional[int] = None
    is_flexible: Optional[bool] = None
    notes: Optional[str] = None

class TrainingSessionResponse(TrainingSessionBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
