from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class PulseItemSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    symbol: str
    name: str
    sector: str
    current_price: float
    checkpoint_price: float
    price_change: float
    price_change_pct: float
    session_change_pct: float = 0.0
    alpha_excess_pct: float
    sector_divergence_pct: float
    volume_z_score: float
    current_volume: int
    avg_volume_20d: int
    attention_score: int
    attention_level: str  # CRITICAL, ELEVATED, ROUTINE
    confidence_score: int
    confidence_tier: str = "HIGH"  # HIGH, MODERATE, ESTABLISHING
    confidence_tier_description: Optional[str] = None
    confidence_breakdown: Dict[str, Any] = Field(default_factory=dict)
    is_meaningful: bool
    primary_drivers: List[str] = Field(default_factory=list)
    summary: str
    breakdown: Dict[str, float] = Field(default_factory=dict)
    related_events: List[Dict[str, Any]] = Field(default_factory=list)


class PulseResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    watchlist_id: str
    watchlist_name: str
    checkpoint_id: str
    checkpoint_time: datetime
    elapsed_seconds: int
    human_elapsed: str
    benchmark_status: Dict[str, Any]
    total_items: int
    meaningful_count: int
    critical_count: int
    executive_summary: str
    items: List[PulseItemSchema]
