from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class WearableConnection(Base):
    __tablename__ = "wearable_connections"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider = Column(String(50), nullable=False)  # "demo", "apple_health", "health_connect", "fitbit"
    display_name = Column(String(100), nullable=False)
    is_connected = Column(Boolean, default=False)
    last_synced_at = Column(DateTime, nullable=True)
    sync_status = Column(String(50), default="idle")  # "idle", "syncing", "success", "error"
    error_message = Column(Text, nullable=True)
    auth_metadata = Column(Text, nullable=True)  # JSON string for tokens or device IDs
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="wearable_connections")

    __table_args__ = (
        UniqueConstraint('user_id', 'provider', name='uq_user_provider'),
    )

class WearableObservation(Base):
    __tablename__ = "wearable_observations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider = Column(String(50), default="demo")
    metric_type = Column(String(50), nullable=False, index=True)  # heart_rate, hrv, steps, resting_hr, sleep_duration, recovery_score
    value = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False)  # bpm, ms, count, hours, score
    recorded_at = Column(DateTime, nullable=False, index=True)
    data_source = Column(String(30), default="SIMULATED_DEMO")  # "WEARABLE_LIVE", "SIMULATED_DEMO", "MANUAL_ENTRY"
    extra_metadata = Column(Text, nullable=True)  # sleep stage, device model, confidence
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="wearable_observations")

    __table_args__ = (
        UniqueConstraint('user_id', 'metric_type', 'recorded_at', 'data_source', name='uq_user_observation'),
    )
