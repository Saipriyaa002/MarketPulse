from datetime import datetime, timedelta, timezone
import pytest
from httpx import AsyncClient
from app.schemas.market import NewsItemSchema
from app.services.event_correlation import EventCorrelationEngine


def test_news_deduplication():
    now = datetime.now(timezone.utc)
    item1 = NewsItemSchema(
        id="N1",
        symbol="INFY",
        headline="Infosys cuts guidance for FY27",
        source_name="Reuters",
        published_at=now,
    )
    # Duplicate with minor spacing/case differences
    item2 = NewsItemSchema(
        id="N2",
        symbol="INFY",
        headline="Infosys cuts guidance for FY27!",
        source_name="Economic Times",
        published_at=now,
    )
    item3 = NewsItemSchema(
        id="N3",
        symbol="TCS",
        headline="TCS wins $500M banking cloud contract",
        source_name="Livemint",
        published_at=now,
    )

    deduped = EventCorrelationEngine.deduplicate_news([item1, item2, item3])
    assert len(deduped) == 2
    assert {d.symbol for d in deduped} == {"INFY", "TCS"}


def test_temporal_delta_window_filtering():
    now = datetime.now(timezone.utc)
    cp_time = now - timedelta(hours=3)

    recent_item = NewsItemSchema(
        id="R1",
        symbol="INFY",
        headline="Recent breaking news",
        source_name="Reuters",
        published_at=now - timedelta(hours=1),
    )
    old_item = NewsItemSchema(
        id="O1",
        symbol="INFY",
        headline="Old event from 2 days ago",
        source_name="Reuters",
        published_at=now - timedelta(days=2),
    )

    filtered = EventCorrelationEngine.filter_by_delta_window([recent_item, old_item], cp_time)
    assert len(filtered) == 1
    assert filtered[0].id == "R1"


def test_sentiment_conflict_detection():
    now = datetime.now(timezone.utc)
    bullish = NewsItemSchema(
        id="B1",
        symbol="HDFCBANK",
        headline="HDFC Bank loan growth surges 18%",
        sentiment_score=0.8,
        source_name="Source A",
        published_at=now,
    )
    bearish = NewsItemSchema(
        id="B2",
        symbol="HDFCBANK",
        headline="NPA provisioning rises, brokerage cuts target",
        sentiment_score=-0.7,
        source_name="Source B",
        published_at=now,
    )

    has_conflict, avg, desc = EventCorrelationEngine.analyze_sentiment_conflict([bullish, bearish])
    assert has_conflict is True
    assert "Conflicting sentiment detected" in desc


@pytest.mark.asyncio
async def test_market_timeline_api(client: AsyncClient):
    res = await client.get("/api/v1/market/timeline?hours=48")
    assert res.status_code == 200
    data = res.json()
    assert "timeline" in data
    assert "sentiment_analysis" in data
    assert data["count"] > 0
