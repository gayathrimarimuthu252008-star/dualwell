from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str = Field(..., min_length=12, max_length=128,
                          description="Password must be at least 12 characters")


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class AccountDeleteRequest(BaseModel):
    password: str = Field(..., min_length=1,
                          description="Current password; required to delete the account")

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None  # access-token lifetime in seconds
    user: UserResponse

class StudentProfileBase(BaseModel):
    age_range: str = "18-22"
    major: str = "Computer Science"
    primary_sport: str = "Rowing / Track & Field"
    usual_sleep_target_hours: float = 8.0
    usual_bedtime: str = "23:00"
    usual_wake_time: str = "07:00"
    daily_hydration_goal_ml: int = 2500
    training_days_per_week: int = 5
    academic_goals: Optional[str] = "Maintain high academic performance and peak athletic recovery"

class StudentProfileCreate(StudentProfileBase):
    pass

class StudentProfileUpdate(BaseModel):
    age_range: Optional[str] = None
    major: Optional[str] = None
    primary_sport: Optional[str] = None
    usual_sleep_target_hours: Optional[float] = None
    usual_bedtime: Optional[str] = None
    usual_wake_time: Optional[str] = None
    daily_hydration_goal_ml: Optional[int] = None
    training_days_per_week: Optional[int] = None
    academic_goals: Optional[str] = None

class StudentProfileResponse(StudentProfileBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PrivacyPreferenceUpdate(BaseModel):
    consent_wearable_sync: Optional[bool] = None
    share_anonymous_metrics: Optional[bool] = None
    allow_overload_notifications: Optional[bool] = None
    allow_hydration_nudges: Optional[bool] = None
    quiet_hours_enabled: Optional[bool] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None

class PrivacyPreferenceResponse(BaseModel):
    id: int
    user_id: int
    consent_wearable_sync: bool
    share_anonymous_metrics: bool
    allow_overload_notifications: bool
    allow_hydration_nudges: bool
    quiet_hours_enabled: bool
    quiet_hours_start: str
    quiet_hours_end: str
    created_at: datetime

    class Config:
        from_attributes = True
