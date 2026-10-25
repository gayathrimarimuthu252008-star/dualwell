from abc import ABC, abstractmethod
from typing import Dict, Any, List
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
    def predict_risk(self, db: Session, user_id: int) -> Dict[str, Any]:
        pass

class RuleBasedExplainableRiskPredictor(BaseRiskPredictor):
    """
    Explainable, transparent heuristic risk prediction engine (v1.0).
    Classifies load into GREEN, YELLOW, and RED tiers and provides
    concrete student-friendly action recommendations.
    
    Advisory Notice: This is a rule-based physiological load estimator
    and is not intended for clinical diagnosis.
    """

    def predict_risk(self, db: Session, user_id: int) -> Dict[str, Any]:
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

        # Record in database for persistence and history
        assessment = RiskAssessment(
            user_id=user_id,
            risk_level=risk_level,
            risk_score=risk_score,
            academic_component=academic_score,
            athletic_component=athletic_score,
            recovery_component=recovery_score,
            factors_summary=summary,
            recommended_actions=json.dumps(actions),
            calculated_at=datetime.utcnow()
        )
        db.add(assessment)
        
        # Also update or insert daily load snapshot
        snapshot = DailyLoadSnapshot(
            user_id=user_id,
            snapshot_date=load_data["target_date"],
            academic_load_score=academic_score,
            athletic_load_score=athletic_score,
            recovery_score=recovery_score,
            dual_load_risk_score=risk_score,
            risk_level=risk_level,
            confidence_score=confidence_score,
            factors_json=json.dumps(factors)
        )
        db.add(snapshot)
        db.commit()

        return {
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

# Default risk predictor instance
risk_predictor: BaseRiskPredictor = RuleBasedExplainableRiskPredictor()
