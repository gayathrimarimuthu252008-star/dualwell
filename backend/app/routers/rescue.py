from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.rescue import RescuePlanResponse
from app.core.deps import get_current_user
from app.services.rescue_engine import PriorityRescueEngine

router = APIRouter(prefix="/rescue", tags=["Priority Rescue Mode"])

@router.get("/plan", response_model=RescuePlanResponse)
def get_rescue_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generates an immediate triage action plan to break cognitive overload in < 60s."""
    return PriorityRescueEngine.generate_plan(db, current_user.id)

@router.post("/regenerate", response_model=RescuePlanResponse)
def regenerate_rescue_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Regenerates the rescue triage plan when commitments or energy change."""
    return PriorityRescueEngine.generate_plan(db, current_user.id)
