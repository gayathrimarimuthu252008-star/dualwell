from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class TrainingSession(Base):
    __tablename__ = "training_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    activity_type = Column(String(50), nullable=False)  # "running", "rowing", "strength", "hiit", "cycling", "mobility", "swimming"
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, default=60)
    intensity = Column(String(20), default="moderate")  # "light", "moderate", "high", "all_out"
    avg_heart_rate = Column(Float, nullable=True)
    max_heart_rate = Column(Float, nullable=True)
    perceived_exertion = Column(Integer, nullable=True)  # RPE 1-10
    is_flexible = Column(Boolean, default=True)  # Can dynamic scheduler recommend adjusting this?
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="training_sessions")
