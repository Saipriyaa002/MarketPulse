from sqlalchemy import Column, DateTime, Float, String
from app.core.database import Base
from app.models.base import utc_now


class Instrument(Base):
    __tablename__ = "instruments"

    symbol = Column(String(50), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    exchange = Column(String(50), default="NSE", nullable=False)
    sector = Column(String(100), nullable=False, index=True)
    industry = Column(String(100), nullable=True)
    beta = Column(Float, default=1.0, nullable=False)
    market_cap = Column(Float, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)
