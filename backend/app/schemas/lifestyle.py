from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class MealLogCreate(BaseModel):
    meal_type: str  # "Breakfast", "Lunch", "Dinner", "Snack", "Pre-workout", "Post-workout"
    description: str
    logged_at: Optional[datetime] = None
    portion_size: str = "Medium"
    calories: Optional[int] = None
    protein_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fat_g: Optional[float] = None

class MealLogResponse(MealLogCreate):
    id: int
    user_id: int
    logged_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True

class HydrationLogCreate(BaseModel):
    amount_ml: int
    logged_at: Optional[datetime] = None

class HydrationQuickAdd(BaseModel):
    amount_ml: int = 250

class HydrationLogResponse(BaseModel):
    id: int
    user_id: int
    amount_ml: int
    logged_at: datetime

    class Config:
        from_attributes = True

class DailyHydrationSummary(BaseModel):
    total_consumed_ml: int
    goal_ml: int
    percentage: float
    recent_logs: List[HydrationLogResponse]
    smart_tip: str

class SleepRecordCreate(BaseModel):
    sleep_start: datetime
    sleep_end: datetime
    duration_hours: float
    deep_sleep_hours: float = 0.0
    rem_sleep_hours: float = 0.0
    light_sleep_hours: float = 0.0
    awake_minutes: int = 0
    efficiency_percentage: float = 85.0
    data_source: str = "MANUAL_ENTRY"
    notes: Optional[str] = None

class SleepRecordResponse(SleepRecordCreate):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class SleepPlanRecommendation(BaseModel):
    target_bedtime: str
    target_wake_time: str
    recommended_winddown_time: str
    sleep_target_hours: float
    actual_average_hours: Optional[float] = None  # 7-day average of real sleep records; None when none logged
    academic_demand_tomorrow: str
    training_demand_tomorrow: str
    advice: str
    has_schedule_conflict: bool

class RecoveryCheckInCreate(BaseModel):
    muscle_soreness: int = 3
    mental_fatigue: int = 3
    sleep_readiness: int = 7
    has_pain_or_strain: bool = False
    pain_details: Optional[str] = None

class RecoveryCheckInResponse(RecoveryCheckInCreate):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
