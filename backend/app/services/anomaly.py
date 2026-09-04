import math
from typing import Dict, Any


class AnomalyEngine:
    @staticmethod
    def calculate_volume_z_score(current_volume: int, avg_volume_20d: int) -> float:
        """
        Calculate volume anomaly Z-score.
        Uses empirical equity standard deviation (approx 35% of 20-day mean volume)
        to detect unusual institutional flow.
        """
        if avg_volume_20d <= 0:
            return 0.0

        volume_ratio = current_volume / avg_volume_20d
        sigma = 0.35 * avg_volume_20d
        z_score = (current_volume - avg_volume_20d) / sigma
        return round(z_score, 2)

    @staticmethod
    def calculate_volatility_spread(high: float, low: float, price: float) -> float:
        """Calculate intraday percentage price spread (High - Low) / Price."""
        if price <= 0:
            return 0.0
        spread_pct = ((high - low) / price) * 100
        return round(spread_pct, 2)
