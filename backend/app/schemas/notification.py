from pydantic import BaseModel
from typing import List
from datetime import datetime

class ReminderCreate(BaseModel):
    title: str
    message: str
    category: str
    scheduled_time: datetime

class ReminderResponse(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    category: str
    scheduled_time: datetime
    is_read: bool
    is_dismissed: bool
    created_at: datetime

    class Config:
        from_attributes = True

class NotificationCenterResponse(BaseModel):
    unread_count: int
    reminders: List[ReminderResponse]
    quiet_hours_active: bool
