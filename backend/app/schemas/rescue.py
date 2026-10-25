from pydantic import BaseModel
from typing import List, Optional

class RescueTaskItem(BaseModel):
    id: str
    order: int
    title: str
    urgency_tier: str  # "NOW", "NEXT", "POSTPONE"
    category: str      # "academic", "training", "wellness", "break"
    duration_minutes: int
    reason: str
    is_completed: bool = False

class RescuePlanResponse(BaseModel):
    is_active: bool
    summary_headline: str
    estimated_energy_level: str  # "Low", "Moderate", "Depleted"
    action_items: List[RescueTaskItem]
    training_adjustment: str
    hydration_nutrition_alert: str
    generated_at: str

class RescueItemToggleRequest(BaseModel):
    item_id: str
    is_completed: bool
