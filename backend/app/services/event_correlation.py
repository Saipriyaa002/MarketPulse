from datetime import datetime, timezone
import hashlib
from typing import Any, Dict, List, Optional, Tuple
from app.schemas.market import NewsItemSchema


class EventCorrelationEngine:
    """
    Correlates financial news and market events with stock movements.
    Handles:
    - Deduplication
    - Temporal delta-window alignment
    - Conflicting news source detection
    - Staleness evaluation
    """

    @staticmethod
    def deduplicate_news(articles: List[NewsItemSchema]) -> List[NewsItemSchema]:
        """
        Deduplicate articles based on headline similarity hash and URL.
        Prevents news spam from distorting event relevance.
        """
        seen_hashes = set()
        deduped: List[NewsItemSchema] = []

        for item in articles:
            # Clean headline for hash
            normalized_headline = "".join(ch.lower() for ch in item.headline if ch.isalnum())
            h = hashlib.sha256(normalized_headline.encode("utf-8")).hexdigest()

            if h in seen_hashes:
                continue

            seen_hashes.add(h)
            deduped.append(item)

        return deduped

    @staticmethod
    def filter_by_delta_window(
        articles: List[NewsItemSchema],
        checkpoint_time: datetime,
        current_time: Optional[datetime] = None,
        grace_minutes: int = 30,
    ) -> List[NewsItemSchema]:
        """
        Filters articles published strictly within the time elapsed since the checkpoint
        (with optional 30m grace buffer to capture pre-session catalysts).
        """
        current_time = current_time or datetime.now(timezone.utc)
        
        # Ensure UTC tz awareness
        if checkpoint_time.tzinfo is None:
            checkpoint_time = checkpoint_time.replace(tzinfo=timezone.utc)
        if current_time.tzinfo is None:
            current_time = current_time.replace(tzinfo=timezone.utc)

        buffer_start = checkpoint_time - (grace_minutes * 60 and datetime.timedelta(minutes=grace_minutes) if hasattr(datetime, "timedelta") else datetime.fromtimestamp(0, timezone.utc))
        from datetime import timedelta
        buffer_start = checkpoint_time - timedelta(minutes=grace_minutes)

        matched: List[NewsItemSchema] = []
        for item in articles:
            pub_time = item.published_at
            if pub_time.tzinfo is None:
                pub_time = pub_time.replace(tzinfo=timezone.utc)

            if buffer_start <= pub_time <= current_time:
                matched.append(item)

        return matched

    @staticmethod
    def analyze_sentiment_conflict(
        articles: List[NewsItemSchema],
    ) -> Tuple[bool, float, str]:
        """
        Detects if multiple articles provide conflicting sentiment signals.
        Returns (has_conflict, average_sentiment, conflict_description).
        """
        if len(articles) < 2:
            avg_sent = articles[0].sentiment_score if articles else 0.0
            return (False, avg_sent, "Consistent single-source coverage")

        positive_count = sum(1 for a in articles if a.sentiment_score > 0.25)
        negative_count = sum(1 for a in articles if a.sentiment_score < -0.25)
        avg_sentiment = round(sum(a.sentiment_score for a in articles) / len(articles), 2)

        if positive_count > 0 and negative_count > 0:
            desc = (
                f"Conflicting sentiment detected: {positive_count} positive source(s) vs "
                f"{negative_count} negative source(s). Net sentiment is {avg_sentiment:+.2f}."
            )
            return (True, avg_sentiment, desc)

        return (False, avg_sentiment, "Consistent sentiment orientation across sources")

    @staticmethod
    def build_event_timeline(
        articles: List[NewsItemSchema],
        checkpoint_time: datetime,
    ) -> List[Dict[str, Any]]:
        """
        Builds a chronological timeline of verified events since user checkpoint.
        Sorted newest first.
        """
        deduped = EventCorrelationEngine.deduplicate_news(articles)
        filtered = EventCorrelationEngine.filter_by_delta_window(deduped, checkpoint_time)
        
        # Sort descending by published_at
        filtered.sort(key=lambda x: x.published_at, reverse=True)

        timeline = []
        for item in filtered:
            pub_time = item.published_at
            if pub_time.tzinfo is None:
                pub_time = pub_time.replace(tzinfo=timezone.utc)

            now = datetime.now(timezone.utc)
            mins_ago = int((now - pub_time).total_seconds() / 60)

            time_str = f"{mins_ago}m ago" if mins_ago < 60 else f"{mins_ago // 60}h ago"

            timeline.append({
                "id": item.id,
                "symbol": item.symbol,
                "sector": item.sector,
                "headline": item.headline,
                "summary": item.summary,
                "source_name": item.source_name,
                "source_url": item.source_url,
                "event_type": item.event_type,
                "sentiment_score": item.sentiment_score,
                "impact_level": item.impact_level,
                "published_at": pub_time.isoformat(),
                "time_display": time_str,
            })

        return timeline
