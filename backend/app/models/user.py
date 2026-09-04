from datetime import datetime
from typing import List, Optional
from sqlalchemy import Boolean, Column, DateTime, String, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import generate_uuid, utc_now


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_guest = Column(Boolean, default=False, nullable=False)
    preferences = Column(JSON, default=dict, nullable=False)  # e.g., {"sensitivity": "medium", "theme": "dark"}
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    watchlists = relationship("Watchlist", back_populates="user", cascade="all, delete-orphan", lazy="selectin")
    checkpoints = relationship("UserCheckpoint", back_populates="user", cascade="all, delete-orphan", lazy="selectin")
