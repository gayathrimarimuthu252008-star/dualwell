from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class MealLog(Base):
    __tablename__ = "meal_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    meal_type = Column(String(50), nullable=False)  # "Breakfast", "Lunch", "Dinner", "Snack", "Pre-workout", "Post-workout"
    description = Column(String(255), nullable=False)
    logged_at = Column(DateTime, default=datetime.utcnow)
    portion_size = Column(String(50), default="Medium")
    calories = Column(Integer, nullable=True)
    protein_g = Column(Float, nullable=True)
    carbs_g = Column(Float, nullable=True)
    fat_g = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="meal_logs")

class HydrationLog(Base):
    __tablename__ = "hydration_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    amount_ml = Column(Integer, nullable=False)
    logged_at = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="hydration_logs")

class SleepRecord(Base):
    __tablename__ = "sleep_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    sleep_start = Column(DateTime, nullable=False)
    sleep_end = Column(DateTime, nullable=False)
    duration_hours = Column(Float, nullable=False)
    deep_sleep_hours = Column(Float, default=0.0)
    rem_sleep_hours = Column(Float, default=0.0)
    light_sleep_hours = Column(Float, default=0.0)
    awake_minutes = Column(Integer, default=0)
    efficiency_percentage = Column(Float, default=85.0)
    data_source = Column(String(30), default="SIMULATED_DEMO")  # "WEARABLE_LIVE", "SIMULATED_DEMO", "MANUAL_ENTRY"
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="sleep_records")

class RecoveryCheckIn(Base):
    __tablename__ = "recovery_checkins"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    muscle_soreness = Column(Integer, default=3)  # 1-10
    mental_fatigue = Column(Integer, default=3)   # 1-10
    sleep_readiness = Column(Integer, default=7)  # 1-10
    has_pain_or_strain = Column(Boolean, default=False)
    pain_details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="recovery_checkins")
