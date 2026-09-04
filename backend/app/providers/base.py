from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional
from app.schemas.market import (
    QuoteSchema,
    OHLCVSchema,
    MarketContextSchema,
    NewsItemSchema,
)


class BaseMarketDataProvider(ABC):
    """Abstract interface for all market data sources."""

    @abstractmethod
    async def get_quotes(self, symbols: List[str]) -> Dict[str, QuoteSchema]:
        """Fetch latest quotes for a batch of symbols."""
        pass

    async def get_quote(self, symbol: str) -> Optional[QuoteSchema]:
        """Fetch latest quote for a single symbol."""
        quotes = await self.get_quotes([symbol])
        return quotes.get(symbol)

    @abstractmethod
    async def get_market_context(self) -> MarketContextSchema:
        """Fetch benchmark index and sector performance data."""
        pass

    @abstractmethod
    async def get_historical_ohlcv(
        self, symbol: str, lookback_days: int = 30
    ) -> List[OHLCVSchema]:
        """Fetch daily/hourly historical OHLCV bars for volatility & volume baselines."""
        pass

    @abstractmethod
    async def get_news(
        self, symbols: Optional[List[str]] = None, since: Optional[datetime] = None
    ) -> List[NewsItemSchema]:
        """Fetch market and stock-specific news items."""
        pass

    @abstractmethod
    async def search_symbols(self, query: str) -> List[Dict[str, str]]:
        """Search available symbols for autocomplete/adding to watchlist."""
        pass
