from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import date, timedelta
from app.database import get_db
from app.models.user import User
from app.models.load_risk import DailyLoadSnapshot
from app.schemas.load_risk import RiskAssessmentResponse, DailyLoadSnapshotResponse
from app.core.deps import get_current_user
from app.services.risk_prediction import risk_predictor
import json

router = APIRouter(prefix="/load-risk", tags=["Dual-Load & Risk Calculation"])

@router.get("/current", response_model=RiskAssessmentResponse)
def get_current_risk(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Computes real-time Dual-Load metrics:
    - Academic Load Score (0-100)
    - Athletic Load Score (0-100)
    - Recovery Score (0-100)
    - Dual-Load Risk Score (0-100)
    - GREEN / YELLOW / RED status with transparent reasoning
    """
    result = risk_predictor.predict_risk(db, current_user.id)
    return result

@router.post("/recalculate", response_model=RiskAssessmentResponse)
def recalculate_risk(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Forces an immediate re-evaluation of load, sleep, and recovery."""
    result = risk_predictor.predict_risk(db, current_user.id)
    return result

@router.get("/history", response_model=List[DailyLoadSnapshotResponse])
def get_load_history(
    days: int = 7,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns chronological historical snapshots for trend visualization."""
    start_date = date.today() - timedelta(days=days)
    snapshots = db.query(DailyLoadSnapshot).filter(
        DailyLoadSnapshot.user_id == current_user.id,
        DailyLoadSnapshot.snapshot_date >= start_date
    ).order_by(DailyLoadSnapshot.snapshot_date.asc()).all()

    response_items = []
    for s in snapshots:
        factors = []
        if s.factors_json:
            try:
                factors = json.loads(s.factors_json)
            except Exception:
                factors = []
        response_items.append({
            "id": s.id,
            "user_id": s.user_id,
            "snapshot_date": s.snapshot_date,
            "academic_load_score": s.academic_load_score,
            "athletic_load_score": s.athletic_load_score,
            "recovery_score": s.recovery_score,
            "dual_load_risk_score": s.dual_load_risk_score,
            "risk_level": s.risk_level,
            "confidence_score": s.confidence_score,
            "factors": factors,
            "created_at": s.created_at
        })
    return response_items
