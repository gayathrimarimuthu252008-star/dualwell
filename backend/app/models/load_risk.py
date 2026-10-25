from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text, Date
from sqlalchemy.orm import relationship
from datetime import datetime, date
from app.database import Base

class DailyLoadSnapshot(Base):
    __tablename__ = "daily_load_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    snapshot_date = Column(Date, default=date.today, index=True)
    academic_load_score = Column(Float, nullable=False)  # 0-100
    athletic_load_score = Column(Float, nullable=False)  # 0-100
    recovery_score = Column(Float, nullable=False)       # 0-100
    dual_load_risk_score = Column(Float, nullable=False) # 0-100
    risk_level = Column(String(20), nullable=False)      # "GREEN", "YELLOW", "RED"
    confidence_score = Column(Float, default=85.0)       # 0-100 %
    factors_json = Column(Text, nullable=True)          # JSON string of factors
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="daily_loads")

class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    risk_level = Column(String(20), nullable=False)  # "GREEN", "YELLOW", "RED"
    risk_score = Column(Float, nullable=False)
    academic_component = Column(Float, nullable=False)
    athletic_component = Column(Float, nullable=False)
    recovery_component = Column(Float, nullable=False)
    factors_summary = Column(Text, nullable=False)
    recommended_actions = Column(Text, nullable=False)  # JSON array of actions
    calculated_at = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="risk_assessments")
