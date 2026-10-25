from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, date, timedelta
from app.database import get_db
from app.models.user import User, StudentProfile
from app.models.lifestyle import MealLog, HydrationLog, SleepRecord, RecoveryCheckIn
from app.models.academic import AcademicEvent
from app.models.training import TrainingSession
from app.schemas.lifestyle import (
    MealLogCreate, MealLogResponse,
    HydrationLogCreate, HydrationQuickAdd, HydrationLogResponse, DailyHydrationSummary,
    SleepRecordCreate, SleepRecordResponse, SleepPlanRecommendation,
    RecoveryCheckInCreate, RecoveryCheckInResponse
)
from app.core.deps import get_current_user

router = APIRouter(prefix="/lifestyle", tags=["Nutrition, Hydration & Sleep"])

# --- MEALS ---
@router.get("/meals", response_model=List[MealLogResponse])
def get_meals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    today_start = datetime.combine(date.today(), datetime.min.time())
    return db.query(MealLog).filter(
        MealLog.user_id == current_user.id,
        MealLog.logged_at >= today_start - timedelta(days=2)
    ).order_by(MealLog.logged_at.desc()).all()

@router.post("/meals", response_model=MealLogResponse, status_code=status.HTTP_201_CREATED)
def log_meal(
    meal_in: MealLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    logged_time = meal_in.logged_at or datetime.utcnow()
    meal = MealLog(
        user_id=current_user.id,
        meal_type=meal_in.meal_type,
        description=meal_in.description,
        logged_at=logged_time,
        portion_size=meal_in.portion_size,
        calories=meal_in.calories,
        protein_g=meal_in.protein_g,
        carbs_g=meal_in.carbs_g,
        fat_g=meal_in.fat_g
    )
    db.add(meal)
    db.commit()
    db.refresh(meal)
    return meal

# --- HYDRATION ---
@router.get("/hydration", response_model=DailyHydrationSummary)
def get_daily_hydration(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    today = datetime.utcnow().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())

    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    goal = profile.daily_hydration_goal_ml if profile else 2500

    logs = db.query(HydrationLog).filter(
        HydrationLog.user_id == current_user.id,
        HydrationLog.logged_at >= today_start,
        HydrationLog.logged_at <= today_end
    ).order_by(HydrationLog.logged_at.desc()).all()

    total = sum(l.amount_ml for l in logs)
    pct = round(min(100.0, (total / goal) * 100.0), 1)

    # Contextual smart tip
    training_today = db.query(TrainingSession).filter(
        TrainingSession.user_id == current_user.id,
        TrainingSession.start_time >= today_start,
        TrainingSession.start_time <= today_end
    ).first()

    if training_today and total < 1500:
        tip = f"Athletic session '{training_today.title}' is on your schedule. Hydrate with an extra 500 mL 90 minutes before start."
    elif total >= goal:
        tip = "Hydration goal achieved for today! Great job sustaining fluid balance for cellular and cognitive function."
    else:
        tip = f"You are at {pct}% of your daily intake target. Sip water regularly between study blocks."

    return DailyHydrationSummary(
        total_consumed_ml=total,
        goal_ml=goal,
        percentage=pct,
        recent_logs=logs,
        smart_tip=tip
    )

@router.post("/hydration", response_model=HydrationLogResponse)
def log_hydration(
    log_in: HydrationLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    log = HydrationLog(
        user_id=current_user.id,
        amount_ml=log_in.amount_ml,
        logged_at=log_in.logged_at or datetime.utcnow()
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log

@router.post("/hydration/quick-add", response_model=DailyHydrationSummary)
def quick_add_hydration(
    quick_in: HydrationQuickAdd,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    log = HydrationLog(
        user_id=current_user.id,
        amount_ml=quick_in.amount_ml,
        logged_at=datetime.utcnow()
    )
    db.add(log)
    db.commit()
    return get_daily_hydration(current_user, db)

# --- SLEEP ---
@router.get("/sleep", response_model=List[SleepRecordResponse])
def get_sleep_records(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(SleepRecord).filter(
        SleepRecord.user_id == current_user.id
    ).order_by(SleepRecord.sleep_end.desc()).limit(14).all()

@router.post("/sleep", response_model=SleepRecordResponse)
def log_sleep_record(
    sleep_in: SleepRecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    rec = SleepRecord(
        user_id=current_user.id,
        **sleep_in.dict()
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec

@router.get("/sleep-plan", response_model=SleepPlanRecommendation)
def get_sleep_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    target_bed = profile.usual_bedtime if profile else "23:00"
    target_wake = profile.usual_wake_time if profile else "07:00"
    target_hrs = profile.usual_sleep_target_hours if profile else 8.0

    # Calculate 45 min earlier winddown
    b_hour, b_min = map(int, target_bed.split(":"))
    b_time = datetime(2026, 1, 1, b_hour, b_min) - timedelta(minutes=45)
    winddown_str = b_time.strftime("%H:%M")

    tomorrow_start = datetime.combine(date.today() + timedelta(days=1), datetime.min.time())
    tomorrow_end = datetime.combine(date.today() + timedelta(days=1), datetime.max.time())

    tomorrow_exams = db.query(AcademicEvent).filter(
        AcademicEvent.user_id == current_user.id,
        AcademicEvent.start_time >= tomorrow_start,
        AcademicEvent.start_time <= tomorrow_end,
        AcademicEvent.event_type == "exam"
    ).all()

    tomorrow_training = db.query(TrainingSession).filter(
        TrainingSession.user_id == current_user.id,
        TrainingSession.start_time >= tomorrow_start,
        TrainingSession.start_time <= tomorrow_end
    ).all()

    # Look for conflicts (e.g. training starting before wake time)
    has_conflict = False
    for tr in tomorrow_training:
        if tr.start_time.hour < b_hour and tr.start_time.hour < int(target_wake.split(":")[0]):
            has_conflict = True

    acad_demand = f"{len(tomorrow_exams)} Exam(s) Scheduled" if tomorrow_exams else "Standard coursework load"
    train_demand = f"{len(tomorrow_training)} Workout(s) planned" if tomorrow_training else "Scheduled recovery day"

    advice = (
        f"To ensure {target_hrs} hours of restorative sleep before tomorrow's {acad_demand.lower()}, "
        f"begin your screen-free wind-down at {winddown_str} and retire by {target_bed}."
    )

    return SleepPlanRecommendation(
        target_bedtime=target_bed,
        target_wake_time=target_wake,
        recommended_winddown_time=winddown_str,
        sleep_target_hours=target_hrs,
        actual_average_hours=7.4,
        academic_demand_tomorrow=acad_demand,
        training_demand_tomorrow=train_demand,
        advice=advice,
        has_schedule_conflict=has_conflict
    )

# --- RECOVERY CHECKIN ---
@router.post("/recovery-checkin", response_model=RecoveryCheckInResponse)
def log_recovery_checkin(
    checkin_in: RecoveryCheckInCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    checkin = RecoveryCheckIn(
        user_id=current_user.id,
        muscle_soreness=checkin_in.muscle_soreness,
        mental_fatigue=checkin_in.mental_fatigue,
        sleep_readiness=checkin_in.sleep_readiness,
        has_pain_or_strain=checkin_in.has_pain_or_strain,
        pain_details=checkin_in.pain_details
    )
    db.add(checkin)
    db.commit()
    db.refresh(checkin)
    return checkin

@router.get("/recovery-checkin/latest", response_model=RecoveryCheckInResponse)
def get_latest_checkin(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    checkin = db.query(RecoveryCheckIn).filter(
        RecoveryCheckIn.user_id == current_user.id
    ).order_by(RecoveryCheckIn.created_at.desc()).first()

    if not checkin:
        # Return default pleasant checkin
        return RecoveryCheckInResponse(
            id=0,
            user_id=current_user.id,
            muscle_soreness=3,
            mental_fatigue=3,
            sleep_readiness=8,
            has_pain_or_strain=False,
            pain_details=None,
            created_at=datetime.utcnow()
        )
    return checkin
