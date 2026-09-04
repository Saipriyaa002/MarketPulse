from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import generate_uuid, utc_now


class Watchlist(Base):
    __tablename__ = "watchlists"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    is_default = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    user = relationship("User", back_populates="watchlists")
    items = relationship("WatchlistItem", back_populates="watchlist", cascade="all, delete-orphan", lazy="selectin")
    checkpoints = relationship("UserCheckpoint", back_populates="watchlist", cascade="all, delete-orphan", lazy="selectin")


class WatchlistItem(Base):
    __tablename__ = "watchlist_items"
    __mapper_args__ = {"confirm_deleted_rows": False}

    id = Column(String(36), primary_key=True, default=generate_uuid)
    watchlist_id = Column(String(36), ForeignKey("watchlists.id", ondelete="CASCADE"), nullable=False, index=True)
    symbol = Column(String(50), nullable=False, index=True)
    custom_tag = Column(String(50), nullable=True)
    alert_preferences = Column(JSON, default=dict, nullable=False)
    added_at = Column(DateTime, default=utc_now, nullable=False)

    # Relationships
    watchlist = relationship("Watchlist", back_populates="items")
