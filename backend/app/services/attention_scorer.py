from typing import Any, Dict, List, Optional
from app.services.change_detection import ChangeDetectionResult
from app.services.confidence import EvidenceConfidenceEngine
from app.schemas.market import NewsItemSchema


class AttentionScorer:
    """
    Computes a composite Attention Score (0-100) and structured Explainability Dossier.
    Never relies on AI for the score; guarantees transparent, deterministic ranking.
    """

    @staticmethod
    def calculate_attention(
        change: ChangeDetectionResult,
        related_news: Optional[List[NewsItemSchema]] = None,
        data_freshness_seconds: int = 15,
        has_checkpoint_baseline: bool = True,
        is_market_closed: bool = False,
    ) -> Dict[str, Any]:
        related_news = related_news or []

        # If price is unchanged since checkpoint (delta ~ 0.0%)
        is_unchanged = abs(change.price_change_pct) < 0.05 and abs(change.alpha_excess_pct) < 0.1 and abs(change.sector_divergence_pct) < 0.1

        # 1. Price / Alpha Component (30% weight)
        if is_unchanged:
            alpha_sub = 0.0
        else:
            alpha_sub = min(100.0, (abs(change.alpha_excess_pct) / 3.0) * 100.0)

        # 2. Sector Divergence Component (20% weight)
        if is_unchanged:
            sector_sub = 0.0
        else:
            sector_sub = min(100.0, (abs(change.sector_divergence_pct) / 2.5) * 100.0)

        # 3. Volume Anomaly Component (20% weight)
        if change.volume_z_score <= 0.0:
            volume_sub = 0.0
        else:
            volume_sub = min(100.0, (change.volume_z_score / 3.0) * 100.0)

        # 4. Event / News Component (20% weight)
        if not related_news:
            event_sub = 0.0
        else:
            max_impact = max(
                (95.0 if n.impact_level == "CRITICAL" else
                 75.0 if n.impact_level == "HIGH" else
                 45.0 if n.impact_level == "MEDIUM" else 20.0)
                for n in related_news
            )
            event_sub = max_impact

        # 5. Volatility / Persistence Component (10% weight)
        if is_unchanged:
            persistence_sub = 0.0
        else:
            persistence_sub = min(100.0, (abs(change.price_change_pct) / 2.0) * 80.0)

        # Total Composite Attention Score (0-100)
        total_raw = (
            (0.30 * alpha_sub) +
            (0.20 * sector_sub) +
            (0.20 * volume_sub) +
            (0.20 * event_sub) +
            (0.10 * persistence_sub)
        )
        total_score = min(100, max(0, int(round(total_raw))))

        # Urgency classification
        if total_score >= 75:
            level = "CRITICAL"
        elif total_score >= 45:
            level = "ELEVATED"
        else:
            level = "ROUTINE"

        # Check for conflicting news sentiment
        has_conflicts = False
        if len(related_news) >= 2:
            pos = any(n.sentiment_score > 0.25 for n in related_news)
            neg = any(n.sentiment_score < -0.25 for n in related_news)
            has_conflicts = pos and neg

        # Defensible Evidence Confidence Evaluation
        confidence_data = EvidenceConfidenceEngine.evaluate(
            data_freshness_seconds=data_freshness_seconds,
            has_checkpoint_baseline=has_checkpoint_baseline,
            has_volume_baseline=change.avg_volume_20d > 0,
            has_sector_benchmark=bool(change.sector_name),
            verified_events_count=len(related_news),
            has_conflicting_events=has_conflicts,
            is_market_closed=is_market_closed,
        )

        # Deterministic evidence summary (works completely without LLM)
        deterministic_summary = AttentionScorer._build_deterministic_summary(
            change, total_score, level, related_news, is_unchanged
        )

        return {
            "score": total_score,
            "level": level,
            "confidence_score": confidence_data["score"],
            "confidence_tier": confidence_data["tier"],
            "confidence_tier_description": confidence_data["tier_description"],
            "confidence_breakdown": confidence_data["breakdown"],
            "breakdown": {
                "market_alpha_score": round(alpha_sub, 1),
                "sector_divergence_score": round(sector_sub, 1),
                "volume_surge_score": round(volume_sub, 1),
                "event_relevance_score": round(event_sub, 1),
                "persistence_score": round(persistence_sub, 1),
            },
            "deterministic_summary": deterministic_summary,
            "primary_drivers": change.primary_drivers,
            "related_events": [
                {
                    "id": n.id,
                    "headline": n.headline,
                    "source": n.source_name,
                    "sentiment": n.sentiment_score,
                    "impact": n.impact_level,
                    "published_at": n.published_at.isoformat(),
                }
                for n in related_news
            ],
        }

    @staticmethod
    def _build_deterministic_summary(
        change: ChangeDetectionResult,
        score: int,
        level: str,
        news: List[NewsItemSchema],
        is_unchanged: bool = False,
    ) -> str:
        """
        Builds a high-quality deterministic narrative purely from facts.
        No hallucination possible because numbers and text are directly bound.
        """
        sym = change.symbol
        delta_sign = "+" if change.price_change_pct >= 0 else ""
        delta_str = f"{delta_sign}{change.price_change_pct:.2f}%"
        alpha_sign = "+" if change.alpha_excess_pct >= 0 else ""
        alpha_str = f"{alpha_sign}{change.alpha_excess_pct:.2f}%"

        if is_unchanged:
            return (
                f"{sym} is currently unchanged at ₹{change.current_price:.2f} ({delta_str}) since your checkpoint. "
                f"Trading is running in line with expected market and sector baselines (Attention Score: {score}/100)."
            )

        parts = []
        if level == "CRITICAL":
            parts.append(
                f"{sym} has experienced a significant movement of {delta_str} since your checkpoint, registering an Attention Score of {score}/100."
            )
        elif level == "ELEVATED":
            parts.append(
                f"{sym} moved {delta_str} since your last checkpoint, showing moderate decoupling from baseline expectations."
            )
        else:
            parts.append(
                f"{sym} is trading at ₹{change.current_price:.2f} ({delta_str}), displaying routine fluctuations consistent with broader market behavior."
            )

        # Context details
        if abs(change.alpha_excess_pct) >= 1.0:
            parts.append(
                f"Adjusted for a Beta of {change.beta:.2f}, its market-relative alpha is {alpha_str} against benchmark."
            )

        if abs(change.sector_divergence_pct) >= 1.0:
            parts.append(
                f"It diverged by {change.sector_divergence_pct:+.2f}% relative to the {change.sector_name} sector."
            )

        if change.volume_z_score >= 1.5:
            parts.append(
                f"Trading activity registered a notable volume anomaly with a Z-score of {change.volume_z_score:.1f}σ."
            )

        # News correlation
        if news:
            top_headline = news[0].headline
            source = news[0].source_name
            parts.append(f"Key catalyst: '{top_headline}' (Source: {source}).")
        else:
            if level in ["CRITICAL", "ELEVATED"]:
                parts.append("No high-confidence catalyst news has been verified during this delta window.")

        return " ".join(parts)
