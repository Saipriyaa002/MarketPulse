from typing import Any, Dict, List, Optional
from app.services.anomaly import AnomalyEngine
from app.schemas.market import QuoteSchema


class ChangeDetectionResult:
    def __init__(
        self,
        symbol: str,
        name: str,
        current_price: float,
        checkpoint_price: float,
        price_change: float,
        price_change_pct: float,
        session_change_pct: float,
        benchmark_change_pct: float,
        expected_market_return_pct: float,
        alpha_excess_pct: float,
        sector_name: str,
        sector_change_pct: float,
        sector_divergence_pct: float,
        current_volume: int,
        avg_volume_20d: int,
        volume_z_score: float,
        beta: float,
        is_meaningful: bool,
        primary_drivers: List[str],
    ):
        self.symbol = symbol
        self.name = name
        self.current_price = current_price
        self.checkpoint_price = checkpoint_price
        self.price_change = price_change
        self.price_change_pct = price_change_pct
        self.session_change_pct = session_change_pct
        self.benchmark_change_pct = benchmark_change_pct
        self.expected_market_return_pct = expected_market_return_pct
        self.alpha_excess_pct = alpha_excess_pct
        self.sector_name = sector_name
        self.sector_change_pct = sector_change_pct
        self.sector_divergence_pct = sector_divergence_pct
        self.current_volume = current_volume
        self.avg_volume_20d = avg_volume_20d
        self.volume_z_score = volume_z_score
        self.beta = beta
        self.is_meaningful = is_meaningful
        self.primary_drivers = primary_drivers

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "name": self.name,
            "current_price": self.current_price,
            "checkpoint_price": self.checkpoint_price,
            "price_change": self.price_change,
            "price_change_pct": self.price_change_pct,
            "session_change_pct": self.session_change_pct,
            "benchmark_change_pct": self.benchmark_change_pct,
            "expected_market_return_pct": self.expected_market_return_pct,
            "alpha_excess_pct": self.alpha_excess_pct,
            "sector_name": self.sector_name,
            "sector_change_pct": self.sector_change_pct,
            "sector_divergence_pct": self.sector_divergence_pct,
            "current_volume": self.current_volume,
            "avg_volume_20d": self.avg_volume_20d,
            "volume_z_score": self.volume_z_score,
            "beta": self.beta,
            "is_meaningful": self.is_meaningful,
            "primary_drivers": self.primary_drivers,
        }


class ChangeDetectionEngine:
    """
    Evaluates market changes strictly over the window since the user's last-seen checkpoint.
    Rejects static price-threshold thinking. Analyzes movements relative to:
    - Market Beta (Alpha / Excess Return over the delta window)
    - Sector Performance (Sector Divergence over the delta window)
    - Institutional Volume Anomaly (Z-Score)
    """

    ALPHA_THRESHOLD: float = 1.2  # 1.2% excess return beyond beta
    SECTOR_DIVERGENCE_THRESHOLD: float = 1.5  # 1.5% divergence from peer group
    VOLUME_Z_THRESHOLD: float = 2.0  # 2.0 standard deviations above 20d mean

    @classmethod
    def evaluate_stock_change(
        cls,
        quote: QuoteSchema,
        checkpoint_item: Optional[Dict[str, Any]],
        benchmark_change_pct: float,
        sector_change_pct: float,
    ) -> ChangeDetectionResult:
        """
        Calculates all deltas over the same window (since checkpoint).
        quote: current live quote
        checkpoint_item: saved quote state at checkpoint
        benchmark_change_pct: benchmark return SINCE CHECKPOINT
        sector_change_pct: sector return SINCE CHECKPOINT
        """
        # Checkpoint baseline price
        if checkpoint_item and "price" in checkpoint_item and checkpoint_item["price"] > 0:
            checkpoint_price = float(checkpoint_item["price"])
        else:
            checkpoint_price = float(quote.previous_close)

        current_price = float(quote.price)
        price_change = round(current_price - checkpoint_price, 2)
        price_change_pct = round(((current_price - checkpoint_price) / checkpoint_price) * 100, 2) if checkpoint_price > 0 else 0.0

        # Beta-adjusted expected return from broad market since checkpoint
        expected_return = round(quote.beta * benchmark_change_pct, 2)
        alpha_excess = round(price_change_pct - expected_return, 2)

        # Sector divergence since checkpoint
        sector_divergence = round(price_change_pct - sector_change_pct, 2)

        # Volume Z-score
        volume_z = AnomalyEngine.calculate_volume_z_score(quote.volume, quote.avg_volume_20d)

        # Multi-factor meaningfulness evaluation
        drivers = []
        is_meaningful = False

        # Check if stock is completely unchanged (e.g. freshly created checkpoint)
        if abs(price_change_pct) < 0.05 and abs(alpha_excess) < 0.1 and abs(sector_divergence) < 0.1:
            drivers.append("Price unchanged since your checkpoint")
        else:
            if abs(alpha_excess) >= cls.ALPHA_THRESHOLD:
                is_meaningful = True
                direction = "outperforming" if alpha_excess > 0 else "underperforming"
                drivers.append(f"Market-relative {direction} (Alpha: {alpha_excess:+.2f}%)")

            if abs(sector_divergence) >= cls.SECTOR_DIVERGENCE_THRESHOLD:
                is_meaningful = True
                direction = "decoupled above" if sector_divergence > 0 else "lagging"
                drivers.append(f"Sector divergence ({direction} {quote.sector} by {sector_divergence:+.2f}%)")

            if volume_z >= cls.VOLUME_Z_THRESHOLD:
                is_meaningful = True
                multiple = round(quote.volume / max(1, quote.avg_volume_20d), 1)
                drivers.append(f"Unusual volume surge ({multiple}x 20-day average, Z-score: {volume_z:.1f}σ)")

        if not drivers:
            drivers.append("Movements within standard expected beta and volatility bands")

        return ChangeDetectionResult(
            symbol=quote.symbol,
            name=quote.name,
            current_price=current_price,
            checkpoint_price=checkpoint_price,
            price_change=price_change,
            price_change_pct=price_change_pct,
            session_change_pct=quote.change_pct,
            benchmark_change_pct=benchmark_change_pct,
            expected_market_return_pct=expected_return,
            alpha_excess_pct=alpha_excess,
            sector_name=quote.sector,
            sector_change_pct=sector_change_pct,
            sector_divergence_pct=sector_divergence,
            current_volume=quote.volume,
            avg_volume_20d=quote.avg_volume_20d,
            volume_z_score=volume_z,
            beta=quote.beta,
            is_meaningful=is_meaningful,
            primary_drivers=drivers,
        )
