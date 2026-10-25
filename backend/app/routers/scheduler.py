from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.scheduler import ScheduleRecommendation
from app.schemas.scheduler import ScheduleRecommendationResponse
from app.core.deps import get_current_user
from app.services.scheduler_engine import DynamicSchedulerEngine

router = APIRouter(prefix="/scheduler", tags=["Smart Dynamic Scheduler"])

@router.get("/recommendations", response_model=List[ScheduleRecommendationResponse])
def get_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    recs = db.query(ScheduleRecommendation).filter(
        ScheduleRecommendation.user_id == current_user.id,
        ScheduleRecommendation.status == "pending"
    ).all()

    if not recs:
        recs = DynamicSchedulerEngine.generate_recommendations(db, current_user.id)

    return recs

@router.post("/generate", response_model=List[ScheduleRecommendationResponse])
def trigger_schedule_optimization(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    recs = DynamicSchedulerEngine.generate_recommendations(db, current_user.id)
    return recs

@router.post("/apply/{rec_id}")
def apply_schedule_recommendation(
    rec_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    success = DynamicSchedulerEngine.apply_recommendation(db, current_user.id, rec_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recommendation could not be applied or was already processed."
        )
    return {"message": "Schedule adjustment successfully applied with student confirmation."}

@router.post("/reject/{rec_id}")
def reject_schedule_recommendation(
    rec_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    success = DynamicSchedulerEngine.reject_recommendation(db, current_user.id, rec_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recommendation could not be rejected or was not found."
        )
    return {"message": "Schedule recommendation dismissed."}
