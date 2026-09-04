import pytest
from app.providers.mock_provider import MockDataProvider


@pytest.mark.asyncio
async def test_mock_provider_quotes():
    provider = MockDataProvider()
    quotes = await provider.get_quotes(["INFY", "TCS", "UNKNOWN_XYZ"])
    
    assert "INFY" in quotes
    assert quotes["INFY"].price > 0
    assert quotes["INFY"].beta == 1.20
    assert quotes["INFY"].sector == "Information Technology"
    assert quotes["INFY"].avg_volume_20d > 0
    assert quotes["INFY"].volume > quotes["INFY"].avg_volume_20d  # Volume surge

    assert "TCS" in quotes
    assert quotes["TCS"].price > 0

    assert "UNKNOWN_XYZ" in quotes
    assert quotes["UNKNOWN_XYZ"].price == 1000.0


@pytest.mark.asyncio
async def test_mock_provider_market_context():
    provider = MockDataProvider()
    context = await provider.get_market_context()
    
    assert context.benchmark_symbol == "NIFTY_50"
    assert context.benchmark_price > 0
    assert "Information Technology" in context.sectors
    assert "Banking & Finance" in context.sectors


@pytest.mark.asyncio
async def test_mock_provider_historical_ohlcv():
    provider = MockDataProvider()
    bars = await provider.get_historical_ohlcv("INFY", lookback_days=15)
    
    assert len(bars) == 15
    for bar in bars:
        assert bar.high >= bar.low
        assert bar.volume > 0


@pytest.mark.asyncio
async def test_mock_provider_news():
    provider = MockDataProvider()
    news = await provider.get_news(symbols=["INFY"])
    
    assert len(news) >= 1
    assert news[0].symbol == "INFY"
    assert news[0].headline != ""
    assert news[0].source_name != ""
