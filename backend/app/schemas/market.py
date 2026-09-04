from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class QuoteSchema(BaseModel):
    symbol: str
    name: str
    price: float
    open: float
    high: float
    low: float
    previous_close: float
    change: float
    change_pct: float
    volume: int
    avg_volume_20d: int
    beta: float = 1.0
    sector: str
    exchange: str = "NSE"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class OHLCVSchema(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int


class SectorPerformanceSchema(BaseModel):
    sector: str
    change_pct: float
    leading_symbol: Optional[str] = None
    lagging_symbol: Optional[str] = None


class MarketContextSchema(BaseModel):
    benchmark_symbol: str = "NIFTY_50"
    benchmark_name: str = "Nifty 50"
    benchmark_price: float
    benchmark_change: float
    benchmark_change_pct: float
    market_status: str = "OPEN"  # OPEN, CLOSED, AFTER_HOURS
    sectors: Dict[str, float] = Field(default_factory=dict)  # sector name -> change_pct
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class NewsItemSchema(BaseModel):
    id: str
    symbol: Optional[str] = None
    sector: Optional[str] = None
    headline: str
    summary: Optional[str] = None
    source_name: str
    source_url: Optional[str] = None
    event_type: str = "general"  # earnings, regulatory, macro, guidance
    sentiment_score: float = 0.0  # -1.0 to 1.0
    impact_level: str = "MEDIUM"  # CRITICAL, HIGH, MEDIUM, LOW
    published_at: datetime
