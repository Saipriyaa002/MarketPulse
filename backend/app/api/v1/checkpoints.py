from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.user import User
from app.models.watchlist import Watchlist
from app.models.checkpoint import UserCheckpoint
from app.schemas.checkpoint import CheckpointAdvanceRequest, CheckpointOut
from app.services.checkpoint import CheckpointService
from app.api.deps import get_current_active_user, get_market_data_provider
from app.providers.base import BaseMarketDataProvider

router = APIRouter()


def format_human_elapsed(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds}s ago"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes}m ago"
    hours = minutes // 60
    rem_min = minutes % 60
    if hours < 24:
        return f"{hours}h {rem_min}m ago" if rem_min > 0 else f"{hours}h ago"
    days = hours // 24
    return f"{days}d ago"


@router.get("/current", response_model=CheckpointOut)
async def get_current_checkpoint(
    watchlist_id: str = Query(..., description="ID of the watchlist"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    provider: BaseMarketDataProvider = Depends(get_market_data_provider),
):
    """Retrieve user's active checkpoint and elapsed time for the specified watchlist."""
    # Verify watchlist ownership
    wl_res = await db.execute(
        select(Watchlist).where(Watchlist.id == watchlist_id, Watchlist.user_id == current_user.id)
    )
    if not wl_res.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Watchlist not found")

    checkpoint = await CheckpointService.get_or_create_latest_checkpoint(
        db, current_user.id, watchlist_id, provider
    )

    now = datetime.now(timezone.utc)
    cp_time = checkpoint.checkpoint_time.replace(tzinfo=timezone.utc) if checkpoint.checkpoint_time.tzinfo is None else checkpoint.checkpoint_time
    elapsed = max(0, int((now - cp_time).total_seconds()))

    return CheckpointOut(
        id=checkpoint.id,
        user_id=checkpoint.user_id,
        watchlist_id=checkpoint.watchlist_id,
        device_id=checkpoint.device_id,
        checkpoint_time=cp_time,
        snapshot_data=checkpoint.snapshot_data,
        trigger_event=checkpoint.trigger_event,
        created_at=checkpoint.created_at,
        elapsed_seconds=elapsed,
        human_elapsed=format_human_elapsed(elapsed),
    )


@router.post("/advance", response_model=CheckpointOut)
async def advance_checkpoint(
    data: CheckpointAdvanceRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    provider: BaseMarketDataProvider = Depends(get_market_data_provider),
):
    """Acknowledge changes and reset the user checkpoint to current moment ('now')."""
    # Verify watchlist ownership
    wl_res = await db.execute(
        select(Watchlist).where(Watchlist.id == data.watchlist_id, Watchlist.user_id == current_user.id)
    )
    if not wl_res.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Watchlist not found")

    new_cp = await CheckpointService.advance_checkpoint(
        db,
        current_user.id,
        data.watchlist_id,
        provider,
        device_id=data.device_id,
        trigger_event=data.trigger_event,
    )

    now = datetime.now(timezone.utc)
    return CheckpointOut(
        id=new_cp.id,
        user_id=new_cp.user_id,
        watchlist_id=new_cp.watchlist_id,
        device_id=new_cp.device_id,
        checkpoint_time=now,
        snapshot_data=new_cp.snapshot_data,
        trigger_event=new_cp.trigger_event,
        created_at=new_cp.created_at,
        elapsed_seconds=0,
        human_elapsed="just now",
    )
