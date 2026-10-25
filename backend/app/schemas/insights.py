from pydantic import BaseModel
from typing import List, Dict

class DailyTrendPoint(BaseModel):
    day: str
    date: str
    academic_load: float
    athletic_load: float
    recovery_score: float
    dual_risk: float
    sleep_hours: float
    hydration_ml: int

class RiskDistribution(BaseModel):
    green_days: int
    yellow_days: int
    red_days: int

class WeeklyInsightsResponse(BaseModel):
    week_range: str
    academic_workload_trend: str
    training_duration_trend: str
    sleep_consistency_score: float
    hydration_logging_consistency: float
    meal_logging_consistency: float
    risk_distribution: RiskDistribution
    recovery_trend_summary: str
    completed_vs_missed_tasks: Dict[str, int]
    daily_trends: List[DailyTrendPoint]
    key_recommendations: List[str]
