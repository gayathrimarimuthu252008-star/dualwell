from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.load_risk import RiskAssessment
from app.core.deps import get_current_user

router = APIRouter(prefix="/recovery-guide", tags=["Recovery & Rehabilitation Guide"])

@router.get("/content")
def get_recovery_guide(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    latest_risk = db.query(RiskAssessment).filter(
        RiskAssessment.user_id == current_user.id
    ).order_by(RiskAssessment.calculated_at.desc()).first()

    rec_score = latest_risk.recovery_component if latest_risk else 75.0

    study_suggestion = {}
    if rec_score >= 75.0:
        study_suggestion = {
            "mode": "High-Cognitive Deep Work Sprint",
            "recommended_duration_min": 60,
            "break_duration_min": 10,
            "focus_type": "Complex problem solving, coding, or mathematical proofs",
            "rationale": "High autonomic recovery and adequate sleep support prolonged prefrontal cortex activation."
        }
    elif rec_score >= 50.0:
        study_suggestion = {
            "mode": "Standard Pomodoro Revision",
            "recommended_duration_min": 35,
            "break_duration_min": 10,
            "focus_type": "Lecture review, flashcard spaced repetition, or essay outlining",
            "rationale": "Moderate recovery. Shorter blocks protect against mid-afternoon cognitive fade."
        }
    else:
        study_suggestion = {
            "mode": "Low-Intensity Active Recall / Reading",
            "recommended_duration_min": 25,
            "break_duration_min": 15,
            "focus_type": "Audio lectures, light reading, organizing notes",
            "rationale": "Elevated fatigue detected. Heavy analytical tasks will yield diminishing returns today."
        }

    return {
        "medical_disclaimer": (
            "IMPORTANT MEDICAL NOTICE: DualWell is an educational wellness aid, not a diagnostic or clinical tool. "
            "Never train through sharp, sudden, or persistent musculoskeletal pain. If experiencing severe symptoms, "
            "stop immediately and seek evaluation from campus health or a licensed physician."
        ),
        "energy_aware_study_suggestion": study_suggestion,
        "gentle_mobility_routines": [
            {
                "id": "mob-1",
                "title": "Thoracic Spine & Posture Reset",
                "duration_minutes": 8,
                "target_area": "Upper Back & Chest (Desk Posture)",
                "steps": [
                    "Seated Thoracic Extensions: Hands behind head, gently arch upper spine over chair back (5 reps)",
                    "Thread the Needle: On hands and knees, reach arm under chest and rotate (30s per side)",
                    "Doorway Pectoral Stretch: Gentle opening of chest muscles (30s)"
                ]
            },
            {
                "id": "mob-2",
                "title": "Hip Flexor & Hamstring Release",
                "duration_minutes": 10,
                "target_area": "Hips & Lower Extremities (Running / Rowing / Long Sitting)",
                "steps": [
                    "Half-Kneeling Hip Flexor Stretch: Engage glute on rear leg, tilt pelvis posterior (45s per side)",
                    "Dynamic Hamstring Sweeps: Heel down, toe up, gentle sweep hands past foot (10 reps each)",
                    "Pigeon Pose or Seated Figure-4: Relieve deep glute tension (45s per side)"
                ]
            },
            {
                "id": "mob-3",
                "title": "Evening Nervous System Parasympathetic Downregulation",
                "duration_minutes": 12,
                "target_area": "Whole Body & Vagal Activation",
                "steps": [
                    "Legs-Up-The-Wall Pose (Viparita Karani): Rest with legs elevated for 5 minutes",
                    "4-7-8 Breathing Cadence: Inhale 4s, hold 7s, exhale 8s (repeat 6 cycles)",
                    "Gentle Neck Lateral Tilts: Slow release of suboccipital tension (30s each side)"
                ]
            }
        ],
        "warmup_guidelines": [
            "Perform 5-7 minutes of progressive general aerobic warm-up (light jog, rowing erg easy pace).",
            "Execute dynamic movement patterns matching today's workout: leg swings, inchworms, lunges with torso twist.",
            "Avoid static stretching immediately prior to heavy explosive lifting or sprinting."
        ],
        "cooldown_guidelines": [
            "Conclude training with 3-5 minutes of low-cadence walking or easy spinning to clear metabolic byproducts.",
            "Rehydrate with 300-500 mL water immediately.",
            "Perform passive static stretches (30-45s holds) while muscle temperature remains elevated."
        ]
    }
