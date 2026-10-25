from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    profile = relationship("StudentProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    privacy = relationship("PrivacyPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")
    wearable_connections = relationship("WearableConnection", back_populates="user", cascade="all, delete-orphan")
    wearable_observations = relationship("WearableObservation", back_populates="user", cascade="all, delete-orphan")
    academic_events = relationship("AcademicEvent", back_populates="user", cascade="all, delete-orphan")
    training_sessions = relationship("TrainingSession", back_populates="user", cascade="all, delete-orphan")
    daily_loads = relationship("DailyLoadSnapshot", back_populates="user", cascade="all, delete-orphan")
    risk_assessments = relationship("RiskAssessment", back_populates="user", cascade="all, delete-orphan")
    schedule_recommendations = relationship("ScheduleRecommendation", back_populates="user", cascade="all, delete-orphan")
    meal_logs = relationship("MealLog", back_populates="user", cascade="all, delete-orphan")
    hydration_logs = relationship("HydrationLog", back_populates="user", cascade="all, delete-orphan")
    sleep_records = relationship("SleepRecord", back_populates="user", cascade="all, delete-orphan")
    reminders = relationship("Reminder", back_populates="user", cascade="all, delete-orphan")
    recovery_checkins = relationship("RecoveryCheckIn", back_populates="user", cascade="all, delete-orphan")

class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    age_range = Column(String(50), default="18-22")
    major = Column(String(100), default="Computer Science")
    primary_sport = Column(String(100), default="Rowing / Track & Field")
    usual_sleep_target_hours = Column(Float, default=8.0)
    usual_bedtime = Column(String(10), default="23:00")
    usual_wake_time = Column(String(10), default="07:00")
    daily_hydration_goal_ml = Column(Integer, default=2500)
    training_days_per_week = Column(Integer, default=5)
    academic_goals = Column(Text, default="Maintain 3.8+ GPA while peaking for collegiate championship")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="profile")

class PrivacyPreference(Base):
    __tablename__ = "privacy_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    consent_wearable_sync = Column(Boolean, default=True)
    share_anonymous_metrics = Column(Boolean, default=False)
    allow_overload_notifications = Column(Boolean, default=True)
    allow_hydration_nudges = Column(Boolean, default=True)
    quiet_hours_enabled = Column(Boolean, default=True)
    quiet_hours_start = Column(String(10), default="22:30")
    quiet_hours_end = Column(String(10), default="06:30")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="privacy")
