from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class ScheduleRecommendation(Base):
    __tablename__ = "schedule_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    related_event_id = Column(Integer, nullable=True)
    event_title = Column(String(200), nullable=False)
    event_category = Column(String(50), default="academic")  # "academic", "training", "break", "sleep"
    original_start_time = Column(DateTime, nullable=True)
    original_end_time = Column(DateTime, nullable=True)
    proposed_start_time = Column(DateTime, nullable=False)
    proposed_end_time = Column(DateTime, nullable=False)
    action_type = Column(String(50), nullable=False)  # "SHIFT_TIME", "INSERT_REST", "INSERT_HYDRATION", "SPLIT_BLOCK", "EARLY_WINDDOWN"
    rationale = Column(Text, nullable=False)
    status = Column(String(20), default="pending")  # "pending", "accepted", "rejected"
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="schedule_recommendations")
