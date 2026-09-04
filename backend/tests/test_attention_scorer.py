from datetime import datetime, timezone
import pytest
from app.schemas.market import NewsItemSchema, QuoteSchema
from app.services.change_detection import ChangeDetectionEngine
from app.services.attention_scorer import AttentionScorer


def test_attention_scorer_critical_event_and_divergence():
    quote = QuoteSchema(
        symbol="INFY",
        name="Infosys",
        price=1800.0,
        open=1850.0,
        high=1860.0,
        low=1790.0,
        previous_close=1890.0,
        change=-90.0,
        change_pct=-4.76,
        volume=15000000,
        avg_volume_20d=5000000,  # 3.0x surge
        beta=1.2,
        sector="Information Technology",
    )

    checkpoint_item = {"price": 1890.0}
    change = ChangeDetectionEngine.evaluate_stock_change(
        quote=quote,
        checkpoint_item=checkpoint_item,
        benchmark_change_pct=-0.2,
        sector_change_pct=-1.0,
    )

    news = [
        NewsItemSchema(
            id="NEWS-01",
            symbol="INFY",
            sector="Information Technology",
            headline="Revenue guidance slashed",
            source_name="Reuters",
            event_type="guidance",
            sentiment_score=-0.8,
            impact_level="CRITICAL",
            published_at=datetime.now(timezone.utc),
        )
    ]

    result = AttentionScorer.calculate_attention(change=change, related_news=news)

    # Score should be high (CRITICAL)
    assert result["score"] >= 75
    assert result["level"] == "CRITICAL"
    assert "deterministic_summary" in result
    assert "Revenue guidance slashed" in result["deterministic_summary"]
    assert "Reuters" in result["deterministic_summary"]
    assert result["confidence_score"] >= 80


def test_attention_scorer_confidence_degradation_on_stale_data():
    quote = QuoteSchema(
        symbol="TCS",
        name="TCS",
        price=4000.0,
        open=4000.0,
        high=4010.0,
        low=3990.0,
        previous_close=4000.0,
        change=0.0,
        change_pct=0.0,
        volume=100000,
        avg_volume_20d=100000,
        beta=1.0,
        sector="Information Technology",
    )
    change = ChangeDetectionEngine.evaluate_stock_change(
        quote=quote,
        checkpoint_item={"price": 4000.0},
        benchmark_change_pct=0.0,
        sector_change_pct=0.0,
    )

    # Fresh data (15 seconds)
    fresh_res = AttentionScorer.calculate_attention(change=change, data_freshness_seconds=15)
    # Stale data (1200 seconds / 20 minutes)
    stale_res = AttentionScorer.calculate_attention(change=change, data_freshness_seconds=1200)

    assert stale_res["confidence_score"] < fresh_res["confidence_score"]
