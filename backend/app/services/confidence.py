from typing import Any, Dict, Optional


class EvidenceConfidenceEngine:
    """
    Computes an auditable, deterministic Evidence Confidence Metric (0-100%)
    with qualitative tiering and transparent factor breakdown.
    Replaces arbitrary fixed precision with real, explainable data-quality dimensions.
    """

    @staticmethod
    def evaluate(
        data_freshness_seconds: int = 15,
        has_checkpoint_baseline: bool = True,
        has_volume_baseline: bool = True,
        has_sector_benchmark: bool = True,
        verified_events_count: int = 0,
        has_conflicting_events: bool = False,
        is_market_closed: bool = False,
    ) -> Dict[str, Any]:
        """
        Calculates confidence across 4 foundational pillars:
        1. Quote Freshness (Max 35)
        2. Baseline Verification (Max 25)
        3. Context Coverage (Max 20)
        4. Catalyst Corroboration (Max 20)
        """
        # 1. Quote Freshness (Max 35)
        if data_freshness_seconds <= 30:
            freshness_score = 35
            freshness_label = "Live stream (<30s)"
        elif data_freshness_seconds <= 180:
            freshness_score = 30
            freshness_label = "Near real-time (<3m)"
        elif data_freshness_seconds <= 900:
            freshness_score = 22
            freshness_label = "Delayed feed (<15m)"
        else:
            freshness_score = 12
            freshness_label = "Stale quote (>15m)"

        # 2. Baseline Verification (Max 25)
        if has_checkpoint_baseline:
            baseline_score = 25
            baseline_label = "Verified user checkpoint"
        else:
            baseline_score = 12
            baseline_label = "Session opening baseline"

        # 3. Context Coverage (Max 20)
        context_score = 0
        if has_volume_baseline:
            context_score += 10
        if has_sector_benchmark:
            context_score += 10
        
        if context_score == 20:
            context_label = "Full sector & volume context"
        elif context_score == 10:
            context_label = "Partial context coverage"
        else:
            context_label = "Baseline establishing"

        # 4. Catalyst Corroboration (Max 20)
        if verified_events_count >= 2 and not has_conflicting_events:
            catalyst_score = 20
            catalyst_label = "Multi-source news corroboration"
        elif verified_events_count == 1 and not has_conflicting_events:
            catalyst_score = 16
            catalyst_label = "Verified single wire report"
        elif has_conflicting_events:
            catalyst_score = 10
            catalyst_label = "Conflicting sentiment across wires"
        else:
            catalyst_score = 12
            catalyst_label = "Pure quantitative order flow (No news catalyst)"

        # Total Calculation
        total = freshness_score + baseline_score + context_score + catalyst_score

        if is_market_closed:
            total = min(total, 85)

        total = max(30, min(100, total))

        if total >= 80:
            tier = "HIGH"
            tier_description = "High confidence backed by fresh quotes, verified baseline, and full market context."
        elif total >= 60:
            tier = "MODERATE"
            tier_description = "Moderate confidence with reliable pricing; some context or catalyst elements rely on estimates."
        else:
            tier = "ESTABLISHING"
            tier_description = "Preliminary baseline being established. Historical anomalies require additional data."

        return {
            "score": total,
            "tier": tier,
            "tier_description": tier_description,
            "breakdown": {
                "quote_freshness": {
                    "points": freshness_score,
                    "max": 35,
                    "label": freshness_label,
                },
                "baseline_integrity": {
                    "points": baseline_score,
                    "max": 25,
                    "label": baseline_label,
                },
                "context_coverage": {
                    "points": context_score,
                    "max": 20,
                    "label": context_label,
                },
                "catalyst_corroboration": {
                    "points": catalyst_score,
                    "max": 20,
                    "label": catalyst_label,
                },
            },
        }
