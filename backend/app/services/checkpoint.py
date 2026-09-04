from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.checkpoint import UserCheckpoint
from app.models.watchlist import Watchlist
from app.providers.base import BaseMarketDataProvider
from app.schemas.checkpoint import CheckpointOut


class CheckpointService:
    @staticmethod
    async def capture_snapshot(
        db: AsyncSession,
        watchlist_id: str,
        provider: BaseMarketDataProvider,
    ) -> Dict[str, Any]:
        """Fetch current prices, volumes, and market context to build a snapshot dictionary."""
        # Load watchlist items
        wl_res = await db.execute(
            select(Watchlist)
            .where(Watchlist.id == watchlist_id)
            .options(selectinload(Watchlist.items))
        )
        watchlist = wl_res.scalar_one_or_none()
        if not watchlist:
            return {}

        symbols = [item.symbol for item in watchlist.items]
        quotes = await provider.get_quotes(symbols) if symbols else {}
        context = await provider.get_market_context()

        now_iso = datetime.now(timezone.utc).isoformat()

        snapshot = {
            "captured_at": now_iso,
            "benchmark": {
                "symbol": context.benchmark_symbol,
                "price": context.benchmark_price,
                "change_pct": context.benchmark_change_pct,
            },
            "sectors": context.sectors,
            "items": {},
        }

        for sym, q in quotes.items():
            snapshot["items"][sym] = {
                "symbol": q.symbol,
                "name": q.name,
                "price": q.price,
                "change_pct": q.change_pct,
                "volume": q.volume,
                "avg_volume_20d": q.avg_volume_20d,
                "beta": q.beta,
                "sector": q.sector,
                "timestamp": q.timestamp.isoformat() if q.timestamp else now_iso,
            }

        return snapshot

    @staticmethod
    async def get_or_create_latest_checkpoint(
        db: AsyncSession,
        user_id: str,
        watchlist_id: str,
        provider: BaseMarketDataProvider,
        device_id: str = "default",
    ) -> UserCheckpoint:
        """Retrieve the user's latest checkpoint, or capture an initial baseline if none exists."""
        result = await db.execute(
            select(UserCheckpoint)
            .where(
                UserCheckpoint.user_id == user_id,
                UserCheckpoint.watchlist_id == watchlist_id,
            )
            .order_by(UserCheckpoint.created_at.desc())
            .limit(1)
        )
        checkpoint = result.scalar_one_or_none()

        if not checkpoint:
            # Create initial baseline checkpoint
            snapshot = await CheckpointService.capture_snapshot(db, watchlist_id, provider)
            checkpoint = UserCheckpoint(
                id=str(uuid.uuid4()),
                user_id=user_id,
                watchlist_id=watchlist_id,
                device_id=device_id,
                checkpoint_time=datetime.now(timezone.utc),
                snapshot_data=snapshot,
                trigger_event="initial_baseline",
            )
            db.add(checkpoint)
            await db.commit()
            await db.refresh(checkpoint)

        return checkpoint

    @staticmethod
    async def advance_checkpoint(
        db: AsyncSession,
        user_id: str,
        watchlist_id: str,
        provider: BaseMarketDataProvider,
        device_id: str = "default",
        trigger_event: str = "manual_ack",
    ) -> UserCheckpoint:
        """Create a new checkpoint representing 'now' (user acknowledges changes)."""
        snapshot = await CheckpointService.capture_snapshot(db, watchlist_id, provider)
        new_checkpoint = UserCheckpoint(
            id=str(uuid.uuid4()),
            user_id=user_id,
            watchlist_id=watchlist_id,
            device_id=device_id,
            checkpoint_time=datetime.now(timezone.utc),
            snapshot_data=snapshot,
            trigger_event=trigger_event,
        )
        db.add(new_checkpoint)
        await db.commit()
        await db.refresh(new_checkpoint)
        return new_checkpoint
