from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, date

class FactorDetail(BaseModel):
    name: str
    impact: str  # "positive", "negative", "neutral"
    description: str
    weight: float

class DailyLoadSnapshotResponse(BaseModel):
    id: int
    user_id: int
    snapshot_date: date
    academic_load_score: float
    athletic_load_score: float
    recovery_score: float
    dual_load_risk_score: float
    risk_level: str  # "GREEN", "YELLOW", "RED"
    confidence_score: float
    factors: List[FactorDetail] = []
    created_at: datetime

    class Config:
        from_attributes = True

class RiskAssessmentResponse(BaseModel):
    risk_level: str  # "GREEN", "YELLOW", "RED"
    risk_score: float
    academic_component: float
    athletic_component: float
    recovery_component: float
    confidence_score: float
    status_headline: str
    factors_summary: str
    contributing_factors: List[FactorDetail]
    recommended_actions: List[str]
    calculated_at: datetime
