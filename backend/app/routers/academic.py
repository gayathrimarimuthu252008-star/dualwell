from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from app.database import get_db
from app.models.user import User
from app.models.academic import AcademicEvent
from app.models.training import TrainingSession
from app.schemas.academic import (
    AcademicEventCreate, AcademicEventUpdate, AcademicEventResponse,
    ConflictResponse, CalendarConflictItem
)
from app.core.deps import get_current_user

router = APIRouter(prefix="/academic", tags=["Academic Calendar & Commitments"])

@router.get("/events", response_model=List[AcademicEventResponse])
def get_academic_events(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(AcademicEvent).filter(
        AcademicEvent.user_id == current_user.id
    ).order_by(AcademicEvent.start_time.asc()).all()

@router.post("/events", response_model=AcademicEventResponse, status_code=status.HTTP_201_CREATED)
def create_academic_event(
    event_in: AcademicEventCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if event_in.end_time <= event_in.start_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Event end time must be after the start time."
        )

    event = AcademicEvent(
        user_id=current_user.id,
        **event_in.dict()
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event

@router.put("/events/{event_id}", response_model=AcademicEventResponse)
def update_academic_event(
    event_id: int,
    event_in: AcademicEventUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    event = db.query(AcademicEvent).filter(
        AcademicEvent.id == event_id,
        AcademicEvent.user_id == current_user.id
    ).first()

    if not event:
        raise HTTPException(status_code=404, detail="Academic event not found.")

    update_data = event_in.dict(exclude_unset=True)
    for field, val in update_data.items():
        setattr(event, field, val)

    if event.end_time <= event.start_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Event end time must be after the start time."
        )

    db.commit()
    db.refresh(event)
    return event

@router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_academic_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    event = db.query(AcademicEvent).filter(
        AcademicEvent.id == event_id,
        AcademicEvent.user_id == current_user.id
    ).first()

    if not event:
        raise HTTPException(status_code=404, detail="Academic event not found.")

    db.delete(event)
    db.commit()
    return None

@router.get("/conflicts", response_model=ConflictResponse)
def detect_conflicts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Detects temporal and recovery conflicts between academic commitments and athletic training.
    """
    now = datetime.utcnow()
    academic_events = db.query(AcademicEvent).filter(
        AcademicEvent.user_id == current_user.id,
        AcademicEvent.start_time >= now - timedelta(days=1),
        AcademicEvent.start_time <= now + timedelta(days=7)
    ).all()

    training_sessions = db.query(TrainingSession).filter(
        TrainingSession.user_id == current_user.id,
        TrainingSession.start_time >= now - timedelta(days=1),
        TrainingSession.start_time <= now + timedelta(days=7)
    ).all()

    conflicts: List[CalendarConflictItem] = []

    # Direct overlap
    for ac in academic_events:
        for tr in training_sessions:
            if ac.start_time < tr.end_time and tr.start_time < ac.end_time:
                conflicts.append(CalendarConflictItem(
                    event_type="academic",
                    title=f"Overlap: {ac.title} vs {tr.title}",
                    start_time=max(ac.start_time, tr.start_time),
                    end_time=min(ac.end_time, tr.end_time),
                    severity="high" if ac.is_fixed else "medium",
                    description=f"Academic commitment '{ac.title}' directly collides with workout '{tr.title}'."
                ))

    # Heavy training immediately before high-stakes exam
    for ac in academic_events:
        if ac.event_type == "exam":
            for tr in training_sessions:
                time_diff = (ac.start_time - tr.end_time).total_seconds() / 3600.0
                if 0 <= time_diff <= 3.0 and tr.intensity in ["high", "all_out"]:
                    conflicts.append(CalendarConflictItem(
                        event_type="training",
                        title=f"Cognitive Fatigue Risk before {ac.title}",
                        start_time=tr.start_time,
                        end_time=tr.end_time,
                        severity="high",
                        description=f"High-intensity training '{tr.title}' finishes only {time_diff:.1f} hours prior to exam '{ac.title}'."
                    ))

    return ConflictResponse(
        has_conflicts=len(conflicts) > 0,
        conflict_count=len(conflicts),
        conflicts=conflicts
    )

@router.get("/export-ics")
def export_icalendar(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Exports student schedule in standard RFC 5545 iCalendar format."""
    events = db.query(AcademicEvent).filter(AcademicEvent.user_id == current_user.id).all()
    
    cal_lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//DualWell//Student Academic Calendar//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH"
    ]

    for ev in events:
        dtstart = ev.start_time.strftime("%Y%m%dT%H%M%SZ")
        dtend = ev.end_time.strftime("%Y%m%dT%H%M%SZ")
        cal_lines.extend([
            "BEGIN:VEVENT",
            f"UID:dualwell-academic-{ev.id}@{current_user.id}",
            f"DTSTAMP:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}",
            f"DTSTART:{dtstart}",
            f"DTEND:{dtend}",
            f"SUMMARY:{ev.title}",
            f"DESCRIPTION:Priority: {ev.priority}. Workload: {ev.estimated_workload_hours}h. Course: {ev.course_name or 'N/A'}",
            f"STATUS:{'COMPLETED' if ev.is_completed else 'CONFIRMED'}",
            "END:VEVENT"
        ])

    cal_lines.append("END:VCALENDAR")
    cal_content = "\r\n".join(cal_lines)

    return Response(
        content=cal_content,
        media_type="text/calendar",
        headers={"Content-Disposition": "attachment; filename=dualwell_academic_calendar.ics"}
    )
