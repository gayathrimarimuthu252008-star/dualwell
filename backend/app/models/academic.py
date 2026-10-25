from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class AcademicEvent(Base):
    __tablename__ = "academic_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    event_type = Column(String(50), nullable=False)  # "exam", "assignment", "class", "study_session", "deadline"
    course_name = Column(String(100), nullable=True)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False)
    priority = Column(String(20), default="medium")  # "low", "medium", "high", "critical"
    estimated_workload_hours = Column(Float, default=2.0)
    is_fixed = Column(Boolean, default=True)  # True for exams, compulsory classes; False for flexible study
    is_completed = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="academic_events")
