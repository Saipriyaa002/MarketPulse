from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.market import QuoteSchema


class WatchlistItemCreate(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=50)
    custom_tag: Optional[str] = None
    alert_preferences: Dict[str, Any] = Field(default_factory=dict)


class WatchlistItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    watchlist_id: str
    symbol: str
    custom_tag: Optional[str] = None
    alert_preferences: Dict[str, Any] = Field(default_factory=dict)
    added_at: datetime
    quote: Optional[QuoteSchema] = None


class WatchlistCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    is_default: bool = False
    symbols: List[str] = Field(default_factory=list)


class WatchlistUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_default: Optional[bool] = None


class WatchlistOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    name: str
    description: Optional[str] = None
    is_default: bool
    created_at: datetime
    updated_at: datetime
    items: List[WatchlistItemOut] = Field(default_factory=list)
