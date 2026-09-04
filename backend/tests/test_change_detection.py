import pytest
from app.schemas.market import QuoteSchema
from app.services.change_detection import ChangeDetectionEngine
from app.services.anomaly import AnomalyEngine


def test_volume_z_score():
    # Normal volume: avg=1,000,000, current=1,000,000 -> Z=0.0
    z_normal = AnomalyEngine.calculate_volume_z_score(1000000, 1000000)
    assert z_normal == 0.0

    # Surge volume: avg=1,000,000, current=2,000,000 -> Z=2.86
    z_surge = AnomalyEngine.calculate_volume_z_score(2000000, 1000000)
    assert z_surge > 2.5


def test_change_detection_beta_adjusted_alpha():
    quote = QuoteSchema(
        symbol="INFY",
        name="Infosys",
        price=100.0,
        open=98.0,
        high=101.0,
        low=97.0,
        previous_close=95.0,
        change=5.0,
        change_pct=5.26,
        volume=2000000,
        avg_volume_20d=1000000,
        beta=1.5,
        sector="Information Technology",
    )

    # Checkpoint baseline was 95.0
    # Current is 100.0 (+5.26%)
    # Benchmark rose +2.0%
    # Expected market return = 1.5 * 2.0% = 3.0%
    # Excess Alpha = 5.26% - 3.0% = +2.26%
    checkpoint_item = {"price": 95.0}
    res = ChangeDetectionEngine.evaluate_stock_change(
        quote=quote,
        checkpoint_item=checkpoint_item,
        benchmark_change_pct=2.0,
        sector_change_pct=1.0,
    )

    assert res.price_change_pct == 5.26
    assert res.expected_market_return_pct == 3.0
    assert res.alpha_excess_pct == 2.26
    assert res.is_meaningful is True
    assert any("Alpha" in d for d in res.primary_drivers)


def test_change_detection_routine_drift():
    quote = QuoteSchema(
        symbol="DEFENSIVE",
        name="Defensive Co",
        price=100.2,
        open=100.0,
        high=100.5,
        low=99.8,
        previous_close=100.0,
        change=0.2,
        change_pct=0.2,
        volume=500000,
        avg_volume_20d=500000,
        beta=1.0,
        sector="FMCG",
    )

    checkpoint_item = {"price": 100.0}
    res = ChangeDetectionEngine.evaluate_stock_change(
        quote=quote,
        checkpoint_item=checkpoint_item,
        benchmark_change_pct=0.1,
        sector_change_pct=0.1,
    )

    assert res.is_meaningful is False
    assert "Movements within standard expected beta" in res.primary_drivers[0]


def test_change_detection_unchanged_since_checkpoint():
    quote = QuoteSchema(
        symbol="INFY",
        name="Infosys",
        price=1845.50,
        open=1840.0,
        high=1855.0,
        low=1835.0,
        previous_close=1890.0,
        change=-44.50,
        change_pct=-2.35,  # Session change
        volume=16400000,
        avg_volume_20d=5800000,
        beta=1.2,
        sector="Information Technology",
    )

    # Checkpoint price equals current price (user checked just now)
    # Benchmark delta since checkpoint is 0.0%
    # Sector delta since checkpoint is 0.0%
    checkpoint_item = {"price": 1845.50}
    res = ChangeDetectionEngine.evaluate_stock_change(
        quote=quote,
        checkpoint_item=checkpoint_item,
        benchmark_change_pct=0.0,
        sector_change_pct=0.0,
    )

    assert res.price_change_pct == 0.0
    assert res.alpha_excess_pct == 0.0
    assert res.sector_divergence_pct == 0.0
    assert res.session_change_pct == -2.35  # Session change preserved for context
    assert res.is_meaningful is False
    assert "Price unchanged since your checkpoint" in res.primary_drivers[0]

