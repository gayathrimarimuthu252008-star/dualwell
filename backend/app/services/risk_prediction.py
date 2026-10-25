from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from app.services.load_engine import DualLoadEngine
from app.models.load_risk import RiskAssessment, DailyLoadSnapshot
import json

class BaseRiskPredictor(ABC):
    """
    Abstract interface for DualWell Overload Risk Prediction services.
    Enables future plug-in replacement with trained machine-learning models
    (e.g., Random Forest or Gradient Boosted Classifiers).
    """
    @abstractmethod
    def compute_risk(self, db: Session, user_id: int) -> Dict[str, Any]:
        """Read-only assessment used by GET /load-risk/current.

        Implementations must not write to the database.
        """
        pass

    @abstractmethod
    def predict_risk(self, db: Session, user_id: int) -> Dict[str, Any]:
        """Assessment plus persistence used by write endpoints (recalculate,
        wearable sync). Upserts exactly one daily snapshot per user per day."""
        pass

class RuleBasedExplainableRiskPredictor(BaseRiskPredictor):
    """
    Explainable, transparent heuristic risk prediction engine (v1.0).
    Classifies load into GREEN, YELLOW, and RED tiers and provides
    concrete student-friendly action recommendations.
    
    Advisory Notice: This is a rule-based physiological load estimator
    and is not intended for clinical diagnosis.
    """

    def _evaluate(self, db: Session, user_id: int) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Computes the full risk assessment without touching the database."""
        load_data = DualLoadEngine.calculate_for_user(db, user_id)
        
        risk_score = load_data["dual_load_risk_score"]
        risk_level = load_data["risk_level"]
        academic_score = load_data["academic_load_score"]
        athletic_score = load_data["athletic_load_score"]
        recovery_score = load_data["recovery_score"]
        confidence_score = load_data["confidence_score"]
        factors = load_data["factors"]

        actions: List[str] = []
        headline = ""
        summary = ""

        if risk_level == "RED":
            headline = "CRITICAL OVERLOAD RISK: Immediate Triage Required"
            summary = (
                f"Combined academic demand ({academic_score:.0f}/100) and athletic strain ({athletic_score:.0f}/100) "
                f"significantly exceed current recovery capacity ({recovery_score:.0f}/100). Fatigue accumulation is high."
            )
            actions = [
                "Activate Priority Rescue Mode to defer non-essential study and training commitments.",
                "Consult training staff or adjust session intensity to light active recovery / mobility only.",
                "Protect an 8-hour sleep window tonight; cease screen work at least 45 minutes before bedtime.",
                "Increase fluid intake by at least 500 mL and schedule 15-minute breaks every 45 minutes of study."
            ]
        elif risk_level == "YELLOW":
            headline = "ELEVATED DUAL LOAD: Proactive Balance Advised"
            summary = (
                f"Your commitments are manageable today ({academic_score:.0f} academic, {athletic_score:.0f} athletic), "
                f"but recovery reserve ({recovery_score:.0f}/100) is tightening. Watch for late-day cognitive exhaustion."
            )
            actions = [
                "Prioritize the highest-urgency coursework during your peak energy hours.",
                "Cap intense training intervals and avoid adding voluntary extra volume today.",
                "Ensure steady hydration and consume a balanced meal with complex carbs before evening study.",
                "Plan wind-down routine 30 minutes earlier to ensure full restorative sleep."
            ]
        else: # GREEN
            headline = "OPTIMAL BALANCE: Readiness is Supportive"
            summary = (
                f"Academic schedule and training volume are well-matched to your recovery readiness ({recovery_score:.0f}/100). "
                "Conditions are favorable for both deep academic work and quality athletic execution."
            )
            actions = [
                "Capitalize on high focus windows for challenging problem sets and deep study.",
                "Execute planned training session with confidence, keeping hydration on target.",
                "Maintain consistent sleep and wake timing to preserve current recovery momentum."
            ]

        result = {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "academic_component": academic_score,
            "athletic_component": athletic_score,
            "recovery_component": recovery_score,
            "confidence_score": confidence_score,
            "status_headline": headline,
            "factors_summary": summary,
            "contributing_factors": factors,
            "recommended_actions": actions,
            "calculated_at": datetime.utcnow()
        }
        return result, load_data

    def compute_risk(self, db: Session, user_id: int) -> Dict[str, Any]:
        """Read-only path for GET /load-risk/current: performs no writes."""
        result, _ = self._evaluate(db, user_id)
        return result

    def predict_risk(self, db: Session, user_id: int) -> Dict[str, Any]:
        """Write path for POST /load-risk/recalculate and wearable sync.

        Records an assessment entry for rescue-mode energy reads and upserts
        the daily load snapshot so there is exactly one row per user per day.
        """
        result, load_data = self._evaluate(db, user_id)
        self._persist(db, user_id, result, load_data)
        return result

    @staticmethod
    def _persist(db: Session, user_id: int, result: Dict[str, Any], load_data: Dict[str, Any]) -> None:
        assessment = RiskAssessment(
            user_id=user_id,
            risk_level=result["risk_level"],
            risk_score=result["risk_score"],
            academic_component=result["academic_component"],
            athletic_component=result["athletic_component"],
            recovery_component=result["recovery_component"],
            factors_summary=result["factors_summary"],
            recommended_actions=json.dumps(result["recommended_actions"]),
            calculated_at=result["calculated_at"]
        )
        db.add(assessment)

        # Upsert: one daily snapshot row per user per day, updated in place.
        snapshot = db.query(DailyLoadSnapshot).filter(
            DailyLoadSnapshot.user_id == user_id,
            DailyLoadSnapshot.snapshot_date == load_data["target_date"]
        ).first()
        if snapshot is None:
            snapshot = DailyLoadSnapshot(
                user_id=user_id,
                snapshot_date=load_data["target_date"]
            )
            db.add(snapshot)
        snapshot.academic_load_score = result["academic_component"]
        snapshot.athletic_load_score = result["athletic_component"]
        snapshot.recovery_score = result["recovery_component"]
        snapshot.dual_load_risk_score = result["risk_score"]
        snapshot.risk_level = result["risk_level"]
        snapshot.confidence_score = result["confidence_score"]
        snapshot.factors_json = json.dumps(result["contributing_factors"])
        db.commit()

# Default risk predictor instance
risk_predictor: BaseRiskPredictor = RuleBasedExplainableRiskPredictor()
