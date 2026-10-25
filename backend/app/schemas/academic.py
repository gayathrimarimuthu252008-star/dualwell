from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AcademicEventBase(BaseModel):
    title: str
    event_type: str  # "exam", "assignment", "class", "study_session", "deadline"
    course_name: Optional[str] = None
    start_time: datetime
    end_time: datetime
    priority: str = "medium"  # "low", "medium", "high", "critical"
    estimated_workload_hours: float = 2.0
    is_fixed: bool = True
    is_completed: bool = False
    notes: Optional[str] = None

class AcademicEventCreate(AcademicEventBase):
    pass

class AcademicEventUpdate(BaseModel):
    title: Optional[str] = None
    event_type: Optional[str] = None
    course_name: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    priority: Optional[str] = None
    estimated_workload_hours: Optional[float] = None
    is_fixed: Optional[bool] = None
    is_completed: Optional[bool] = None
    notes: Optional[str] = None

class AcademicEventResponse(AcademicEventBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CalendarConflictItem(BaseModel):
    event_type: str  # "academic" or "training"
    title: str
    start_time: datetime
    end_time: datetime
    severity: str  # "high", "medium"
    description: str

class ConflictResponse(BaseModel):
    has_conflicts: bool
    conflict_count: int
    conflicts: list[CalendarConflictItem]
