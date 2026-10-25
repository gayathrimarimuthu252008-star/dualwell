from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.insights import WeeklyInsightsResponse
from app.core.deps import get_current_user
from app.services.insights_engine import WeeklyInsightsEngine

router = APIRouter(prefix="/insights", tags=["Weekly Analytics & Insights"])

@router.get("/weekly", response_model=WeeklyInsightsResponse)
def get_weekly_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns 7-day comprehensive analytics on academic load, training volume,
    sleep consistency, hydration streaks, and recovery trends.
    """
    return WeeklyInsightsEngine.generate_weekly_report(db, current_user.id)
