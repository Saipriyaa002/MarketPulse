from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.providers.base import BaseMarketDataProvider
from app.api.deps import get_market_data_provider
from app.schemas.market import (
    QuoteSchema,
    OHLCVSchema,
    MarketContextSchema,
    NewsItemSchema,
)

router = APIRouter()


@router.get("/quotes", response_model=Dict[str, QuoteSchema])
async def get_quotes(
    symbols: str = Query(..., description="Comma-separated ticker symbols, e.g. INFY,TCS,RELIANCE"),
    provider: BaseMarketDataProvider = Depends(get_market_data_provider),
):
    """Retrieve current quotes for multiple symbols."""
    symbol_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]
    if not symbol_list:
        return {}
    return await provider.get_quotes(symbol_list)


@router.get("/quote/{symbol}", response_model=QuoteSchema)
async def get_single_quote(
    symbol: str,
    provider: BaseMarketDataProvider = Depends(get_market_data_provider),
):
    """Retrieve quote for a single symbol."""
    quote = await provider.get_quote(symbol.strip().upper())
    if not quote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quote for symbol '{symbol}' not found",
        )
    return quote


@router.get("/context", response_model=MarketContextSchema)
async def get_market_context(
    provider: BaseMarketDataProvider = Depends(get_market_data_provider),
):
    """Retrieve broad market benchmark index status and sector performance."""
    return await provider.get_market_context()


@router.get("/history/{symbol}", response_model=List[OHLCVSchema])
async def get_historical_ohlcv(
    symbol: str,
    days: int = Query(30, ge=5, le=365, description="Lookback days"),
    provider: BaseMarketDataProvider = Depends(get_market_data_provider),
):
    """Retrieve historical daily OHLCV bars."""
    return await provider.get_historical_ohlcv(symbol.strip().upper(), lookback_days=days)


@router.get("/news", response_model=List[NewsItemSchema])
async def get_market_news(
    symbols: Optional[str] = Query(None, description="Optional comma-separated symbols to filter"),
    provider: BaseMarketDataProvider = Depends(get_market_data_provider),
):
    """Retrieve verified financial news items."""
    sym_list = [s.strip().upper() for s in symbols.split(",") if s.strip()] if symbols else None
    return await provider.get_news(symbols=sym_list)


@router.get("/timeline")
async def get_market_timeline(
    symbols: Optional[str] = Query(None, description="Comma-separated symbols to include"),
    hours: float = Query(24.0, ge=0.5, le=168.0, description="Lookback window in hours"),
    provider: BaseMarketDataProvider = Depends(get_market_data_provider),
):
    """Retrieve chronologically organized event timeline with conflict analysis."""
    from datetime import datetime, timedelta, timezone
    from app.services.event_correlation import EventCorrelationEngine

    sym_list = [s.strip().upper() for s in symbols.split(",") if s.strip()] if symbols else None
    since_time = datetime.now(timezone.utc) - timedelta(hours=hours)

    raw_news = await provider.get_news(symbols=sym_list, since=since_time)
    timeline = EventCorrelationEngine.build_event_timeline(raw_news, checkpoint_time=since_time)
    has_conflict, avg_sentiment, conflict_desc = EventCorrelationEngine.analyze_sentiment_conflict(raw_news)

    return {
        "timeline": timeline,
        "count": len(timeline),
        "lookback_hours": hours,
        "sentiment_analysis": {
            "has_conflict": has_conflict,
            "average_sentiment": avg_sentiment,
            "description": conflict_desc,
        },
    }


@router.get("/search", response_model=List[Dict[str, str]])
async def search_symbols(
    q: str = Query(..., min_length=1, description="Search query ticker or company name"),
    provider: BaseMarketDataProvider = Depends(get_market_data_provider),
):
    """Search catalog of stocks for autocomplete."""
    return await provider.search_symbols(q)
