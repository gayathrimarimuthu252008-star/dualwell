from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta, time
from app.database import get_db
from app.models.user import User, PrivacyPreference
from app.models.notification import Reminder
from app.models.academic import AcademicEvent
from app.models.training import TrainingSession
from app.schemas.notification import ReminderResponse, NotificationCenterResponse
from app.core.deps import get_current_user

router = APIRouter(prefix="/notifications", tags=["Smart Reminders & In-App Alarms"])

@router.get("/reminders", response_model=NotificationCenterResponse)
def get_reminders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if quiet hours are currently active
    privacy = db.query(PrivacyPreference).filter(PrivacyPreference.user_id == current_user.id).first()
    is_quiet_active = False
    if privacy and privacy.quiet_hours_enabled:
        now_time = datetime.utcnow().time()
        start_h, start_m = map(int, privacy.quiet_hours_start.split(":"))
        end_h, end_m = map(int, privacy.quiet_hours_end.split(":"))
        q_start = time(start_h, start_m)
        q_end = time(end_h, end_m)
        if q_start > q_end:
            # crosses midnight
            is_quiet_active = (now_time >= q_start or now_time <= q_end)
        else:
            is_quiet_active = (q_start <= now_time <= q_end)

    reminders = db.query(Reminder).filter(
        Reminder.user_id == current_user.id,
        Reminder.is_dismissed == False
    ).order_by(Reminder.scheduled_time.asc()).all()

    # If empty, generate contextual smart reminders
    if not reminders:
        reminders = generate_smart_reminders_internal(db, current_user.id)

    unread_count = sum(1 for r in reminders if not r.is_read)

    return NotificationCenterResponse(
        unread_count=unread_count,
        reminders=reminders,
        quiet_hours_active=is_quiet_active
    )

def generate_smart_reminders_internal(db: Session, user_id: int) -> List[Reminder]:
    now = datetime.utcnow()
    created = []

    # 1. Hydration prompt
    r1 = Reminder(
        user_id=user_id,
        title="Hydration Check-in",
        message="Keep your fluid intake steady. Log a quick glass (250 mL) to maintain cellular recovery.",
        category="HYDRATION",
        scheduled_time=now + timedelta(minutes=45)
    )
    db.add(r1)
    created.append(r1)

    # 2. Upcoming academic deadline or study block
    urgent_academic = db.query(AcademicEvent).filter(
        AcademicEvent.user_id == user_id,
        AcademicEvent.start_time >= now,
        AcademicEvent.start_time <= now + timedelta(hours=24)
    ).order_by(AcademicEvent.start_time.asc()).first()

    if urgent_academic:
        r2 = Reminder(
            user_id=user_id,
            title=f"Upcoming: {urgent_academic.title}",
            message=f"Scheduled for {urgent_academic.start_time.strftime('%I:%M %p')}. Prepare course notes and water.",
            category="EXAM_DEADLINE" if urgent_academic.event_type == "exam" else "STUDY_BREAK",
            scheduled_time=urgent_academic.start_time - timedelta(minutes=30)
        )
        db.add(r2)
        created.append(r2)

    # 3. Training prompt
    train_soon = db.query(TrainingSession).filter(
        TrainingSession.user_id == user_id,
        TrainingSession.start_time >= now,
        TrainingSession.start_time <= now + timedelta(hours=24)
    ).order_by(TrainingSession.start_time.asc()).first()

    if train_soon:
        r3 = Reminder(
            user_id=user_id,
            title=f"Training Warm-Up: {train_soon.title}",
            message="Time for pre-workout mobility and dynamic stretching. Review heart rate intensity targets.",
            category="TRAINING",
            scheduled_time=train_soon.start_time - timedelta(minutes=15)
        )
        db.add(r3)
        created.append(r3)

    # 4. Sleep preparation
    r4 = Reminder(
        user_id=user_id,
        title="Evening Wind-Down",
        message="Target bedtime is approaching. Shut down bright screens and initiate low-stimulation routine.",
        category="SLEEP_PREP",
        scheduled_time=now + timedelta(hours=4)
    )
    db.add(r4)
    created.append(r4)

    db.commit()
    for r in created:
        db.refresh(r)
    return created

@router.post("/reminders/{reminder_id}/read", response_model=ReminderResponse)
def mark_reminder_read(
    reminder_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    rem = db.query(Reminder).filter(
        Reminder.id == reminder_id,
        Reminder.user_id == current_user.id
    ).first()

    if not rem:
        raise HTTPException(status_code=404, detail="Reminder not found.")

    rem.is_read = True
    db.commit()
    db.refresh(rem)
    return rem

@router.post("/reminders/{reminder_id}/dismiss")
def dismiss_reminder(
    reminder_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    rem = db.query(Reminder).filter(
        Reminder.id == reminder_id,
        Reminder.user_id == current_user.id
    ).first()

    if not rem:
        raise HTTPException(status_code=404, detail="Reminder not found.")

    rem.is_dismissed = True
    db.commit()
    return {"message": "Reminder dismissed."}
