from sqlalchemy import Column, DateTime, Float, String, JSON
from app.core.database import Base
from app.models.base import generate_uuid, utc_now


class MarketEvent(Base):
    __tablename__ = "market_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    symbol = Column(String(50), nullable=True, index=True)
    sector = Column(String(100), nullable=True, index=True)
    headline = Column(String(500), nullable=False)
    summary = Column(String(1500), nullable=True)
    source_name = Column(String(100), nullable=False)
    source_url = Column(String(500), nullable=True)
    event_type = Column(String(50), default="general", nullable=False)
    sentiment_score = Column(Float, default=0.0, nullable=False)
    impact_level = Column(String(20), default="MEDIUM", nullable=False)
    published_at = Column(DateTime, default=utc_now, nullable=False, index=True)
    raw_metadata = Column(JSON, default=dict, nullable=False)
