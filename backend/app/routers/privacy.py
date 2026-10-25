from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
import json
from app.database import get_db
from app.models.user import User, PrivacyPreference, StudentProfile
from app.models.academic import AcademicEvent
from app.models.training import TrainingSession
from app.models.lifestyle import MealLog, HydrationLog, SleepRecord, RecoveryCheckIn
from app.models.wearable import WearableConnection, WearableObservation
from app.schemas.user import PrivacyPreferenceResponse, PrivacyPreferenceUpdate, AccountDeleteRequest
from app.core.deps import get_current_user
from app.core.security import verify_password

router = APIRouter(prefix="/privacy", tags=["Privacy Controls & Data Governance"])

@router.get("/settings", response_model=PrivacyPreferenceResponse)
def get_privacy_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    priv = db.query(PrivacyPreference).filter(PrivacyPreference.user_id == current_user.id).first()
    if not priv:
        priv = PrivacyPreference(user_id=current_user.id)
        db.add(priv)
        db.commit()
        db.refresh(priv)
    return priv

@router.put("/settings", response_model=PrivacyPreferenceResponse)
def update_privacy_settings(
    priv_in: PrivacyPreferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    priv = db.query(PrivacyPreference).filter(PrivacyPreference.user_id == current_user.id).first()
    if not priv:
        priv = PrivacyPreference(user_id=current_user.id)
        db.add(priv)

    update_dict = priv_in.model_dump(exclude_unset=True)
    for field, val in update_dict.items():
        setattr(priv, field, val)

    db.commit()
    db.refresh(priv)
    return priv

@router.get("/export-data")
def export_student_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Exports all personal student records as a structured JSON archive
    complying with data portability and GDPR/FERPA guidelines.
    """
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    academic = db.query(AcademicEvent).filter(AcademicEvent.user_id == current_user.id).all()
    training = db.query(TrainingSession).filter(TrainingSession.user_id == current_user.id).all()
    meals = db.query(MealLog).filter(MealLog.user_id == current_user.id).all()
    water = db.query(HydrationLog).filter(HydrationLog.user_id == current_user.id).all()
    sleep = db.query(SleepRecord).filter(SleepRecord.user_id == current_user.id).all()
    checkins = db.query(RecoveryCheckIn).filter(RecoveryCheckIn.user_id == current_user.id).all()
    wearables = db.query(WearableConnection).filter(WearableConnection.user_id == current_user.id).all()
    observations = db.query(WearableObservation).filter(WearableObservation.user_id == current_user.id).all()

    export_payload = {
        "export_metadata": {
            "application": "DualWell: Smart Student Wellness and Academic Performance System",
            "student_id": current_user.id,
            "student_email": current_user.email,
            "student_name": current_user.full_name,
            "exported_at": str(db.query(User).filter(User.id == current_user.id).first().updated_at)
        },
        "student_profile": {
            "major": profile.major if profile else None,
            "sport": profile.primary_sport if profile else None,
            "sleep_target_hours": profile.usual_sleep_target_hours if profile else 8.0,
            "hydration_target_ml": profile.daily_hydration_goal_ml if profile else 2500
        },
        "academic_events": [
            {"id": e.id, "title": e.title, "type": e.event_type, "start": str(e.start_time), "end": str(e.end_time), "priority": e.priority}
            for e in academic
        ],
        "training_sessions": [
            {"id": t.id, "title": t.title, "sport": t.activity_type, "start": str(t.start_time), "duration_min": t.duration_minutes, "intensity": t.intensity}
            for t in training
        ],
        "meals": [
            {"type": m.meal_type, "desc": m.description, "calories": m.calories, "time": str(m.logged_at)}
            for m in meals
        ],
        "hydration_logs": [
            {"amount_ml": h.amount_ml, "time": str(h.logged_at)}
            for h in water
        ],
        "sleep_records": [
            {"start": str(s.sleep_start), "end": str(s.sleep_end), "duration_h": s.duration_hours, "source": s.data_source}
            for s in sleep
        ],
        "fatigue_checkins": [
            {"muscle_soreness": c.muscle_soreness, "mental_fatigue": c.mental_fatigue, "pain": c.has_pain_or_strain, "time": str(c.created_at)}
            for c in checkins
        ],
        "wearable_telemetry_summary": {
            "total_observations": len(observations),
            "connected_devices": [w.provider for w in wearables if w.is_connected]
        }
    }

    json_str = json.dumps(export_payload, indent=2)
    return Response(
        content=json_str,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=dualwell_student_data_export_{current_user.id}.json"}
    )

@router.delete("/delete-account")
def delete_student_account(
    payload: AccountDeleteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Permanently purges student account and all linked records.

    Requires the account password in the request body: an active session alone
    is not enough to destroy data (protects against session hijacking/XSS).
    """
    if not verify_password(payload.password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Password incorrect. Account deletion cancelled."
        )

    db.delete(current_user)
    db.commit()
    return {"message": "Account and all associated records have been permanently erased."}
