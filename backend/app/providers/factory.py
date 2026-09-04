from app.core.config import settings
from app.providers.base import BaseMarketDataProvider
from app.providers.mock_provider import MockDataProvider

_provider_instance: BaseMarketDataProvider | None = None


def get_market_provider() -> BaseMarketDataProvider:
    """Singleton getter for the configured market data provider."""
    global _provider_instance
    if _provider_instance is None:
        if settings.DEFAULT_MARKET_PROVIDER == "mock":
            _provider_instance = MockDataProvider()
        else:
            # Default to mock provider for reliability unless explicitly configured
            _provider_instance = MockDataProvider()
    return _provider_instance
