from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.training import TrainingSession
from app.schemas.training import TrainingSessionCreate, TrainingSessionUpdate, TrainingSessionResponse
from app.core.deps import get_current_user

router = APIRouter(prefix="/training", tags=["Athletic Training"])

@router.get("/sessions", response_model=List[TrainingSessionResponse])
def get_training_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(TrainingSession).filter(
        TrainingSession.user_id == current_user.id
    ).order_by(TrainingSession.start_time.asc()).all()

@router.post("/sessions", response_model=TrainingSessionResponse, status_code=status.HTTP_201_CREATED)
def create_training_session(
    session_in: TrainingSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if session_in.end_time <= session_in.start_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Training end time must be after start time."
        )

    ts = TrainingSession(
        user_id=current_user.id,
        **session_in.dict()
    )
    db.add(ts)
    db.commit()
    db.refresh(ts)
    return ts

@router.put("/sessions/{session_id}", response_model=TrainingSessionResponse)
def update_training_session(
    session_id: int,
    session_in: TrainingSessionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ts = db.query(TrainingSession).filter(
        TrainingSession.id == session_id,
        TrainingSession.user_id == current_user.id
    ).first()

    if not ts:
        raise HTTPException(status_code=404, detail="Training session not found.")

    update_data = session_in.dict(exclude_unset=True)
    for field, val in update_data.items():
        setattr(ts, field, val)

    if ts.end_time <= ts.start_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Training end time must be after start time."
        )

    db.commit()
    db.refresh(ts)
    return ts

@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_training_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ts = db.query(TrainingSession).filter(
        TrainingSession.id == session_id,
        TrainingSession.user_id == current_user.id
    ).first()

    if not ts:
        raise HTTPException(status_code=404, detail="Training session not found.")

    db.delete(ts)
    db.commit()
    return None
