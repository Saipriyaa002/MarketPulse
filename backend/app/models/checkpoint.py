from sqlalchemy import Column, DateTime, ForeignKey, String, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import generate_uuid, utc_now


class UserCheckpoint(Base):
    __tablename__ = "user_checkpoints"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    watchlist_id = Column(String(36), ForeignKey("watchlists.id", ondelete="CASCADE"), nullable=False, index=True)
    device_id = Column(String(100), default="default", nullable=False)
    checkpoint_time = Column(DateTime, default=utc_now, nullable=False, index=True)
    snapshot_data = Column(JSON, default=dict, nullable=False)
    trigger_event = Column(String(50), default="manual_ack", nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    # Relationships
    user = relationship("User", back_populates="checkpoints")
    watchlist = relationship("Watchlist", back_populates="checkpoints")
