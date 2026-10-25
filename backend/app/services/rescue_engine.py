from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from app.models.academic import AcademicEvent
from app.models.training import TrainingSession
from app.models.lifestyle import SleepRecord, RecoveryCheckIn
from app.models.load_risk import RiskAssessment
from app.schemas.rescue import RescuePlanResponse, RescueTaskItem

class PriorityRescueEngine:
    """
    Emergency triage engine for overloaded students.
    Cuts through cognitive overload within 60 seconds with an immediate,
    uncluttered, non-negotiable prioritization matrix:
    - 1. DO NOW (Single focused task, 30-45m)
    - 2. DO NEXT (Upcoming urgent checkpoint)
    - 3. POSTPONE (Permissible items safely pushed back to reduce acute load)
    - Training modulation & hydration/recovery intervention.
    """

    @classmethod
    def generate_plan(cls, db: Session, user_id: int) -> RescuePlanResponse:
        now = datetime.utcnow()
        today_end = now + timedelta(hours=18)

        # 1. Gather pending academic tasks ordered by urgency
        academic_events = db.query(AcademicEvent).filter(
            AcademicEvent.user_id == user_id,
            AcademicEvent.is_completed == False,
            AcademicEvent.start_time <= today_end
        ).order_by(
            AcademicEvent.priority.desc(),
            AcademicEvent.start_time.asc()
        ).all()

        # 2. Gather training sessions
        training_sessions = db.query(TrainingSession).filter(
            TrainingSession.user_id == user_id,
            TrainingSession.start_time >= now - timedelta(hours=2),
            TrainingSession.start_time <= today_end
        ).all()

        # 3. Assess energy level
        latest_risk = db.query(RiskAssessment).filter(
            RiskAssessment.user_id == user_id
        ).order_by(RiskAssessment.calculated_at.desc()).first()

        energy_level = "Moderate"
        if latest_risk and latest_risk.risk_level == "RED":
            energy_level = "Depleted"
        elif latest_risk and latest_risk.risk_level == "GREEN":
            energy_level = "Sufficient"

        # 4. Synthesize Action Items
        items: List[RescueTaskItem] = []

        # Urgent academic item
        if academic_events:
            top_task = academic_events[0]
            items.append(RescueTaskItem(
                id="rescue-now-1",
                order=1,
                title=f"Focused Study Sprint: {top_task.title}",
                urgency_tier="NOW",
                category="academic",
                duration_minutes=35,
                reason="Immediate deadline / highest priority academic deliverable. Work in one uninterrupted 35-min block."
            ))

            if len(academic_events) > 1:
                second_task = academic_events[1]
                items.append(RescueTaskItem(
                    id="rescue-next-1",
                    order=2,
                    title=f"Review & Checkpoint: {second_task.title}",
                    urgency_tier="NEXT",
                    category="academic",
                    duration_minutes=25,
                    reason="Second in priority. Address after a mandatory 10-minute mental break."
                ))

            if len(academic_events) > 2:
                for idx, post_task in enumerate(academic_events[2:4]):
                    items.append(RescueTaskItem(
                        id=f"rescue-postpone-{idx}",
                        order=3 + idx,
                        title=f"Defer {post_task.title}",
                        urgency_tier="POSTPONE",
                        category="academic",
                        duration_minutes=0,
                        reason="Lower immediate consequence. Postponing lowers acute cognitive overload by 40%."
                    ))
        else:
            items.append(RescueTaskItem(
                id="rescue-now-default",
                order=1,
                title="Academic Inbox Zero & Course Material Review",
                urgency_tier="NOW",
                category="academic",
                duration_minutes=30,
                reason="No urgent deadlines found. Clear current lecture notes and organize study deck."
            ))

        # Training adjustment suggestion
        training_adjustment = ""
        if any(tr.is_flexible for tr in training_sessions):
            if energy_level == "Depleted":
                training_adjustment = (
                    "RECOMMENDATION: Downgrade planned high-intensity workout to a 20-minute gentle "
                    "mobility / foam rolling session. Defer heavy anaerobic sets to avoid neuro-muscular breakdown."
                )
            else:
                training_adjustment = (
                    "RECOMMENDATION: Reduce planned training volume by 25%. Maintain moderate pace and "
                    "focus on active recovery intervals."
                )
        else:
            training_adjustment = (
                "Ensure thorough 15-minute cool-down and post-workout protein intake. "
                "No optional extra workouts today."
            )

        hydration_nutrition_alert = (
            "Drink 500 mL water immediately with electrolytes if available. "
            "Consume a snack containing protein and complex carbohydrates to stabilize blood sugar and cognitive clarity."
        )

        return RescuePlanResponse(
            is_active=True,
            summary_headline=f"Rescue Mode Active — Energy Level: {energy_level}",
            estimated_energy_level=energy_level,
            action_items=items,
            training_adjustment=training_adjustment,
            hydration_nutrition_alert=hydration_nutrition_alert,
            generated_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        )
