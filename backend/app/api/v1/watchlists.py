import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.models.user import User
from app.models.watchlist import Watchlist, WatchlistItem
from app.schemas.watchlist import (
    WatchlistCreate,
    WatchlistOut,
    WatchlistUpdate,
    WatchlistItemCreate,
    WatchlistItemOut,
)
from app.api.deps import get_current_active_user, get_market_data_provider
from app.providers.base import BaseMarketDataProvider

router = APIRouter()


@router.get("", response_model=List[WatchlistOut])
async def list_watchlists(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    provider: BaseMarketDataProvider = Depends(get_market_data_provider),
):
    """Retrieve all watchlists for the logged-in user with latest quotes."""
    result = await db.execute(
        select(Watchlist)
        .where(Watchlist.user_id == current_user.id)
        .options(selectinload(Watchlist.items))
        .order_by(Watchlist.is_default.desc(), Watchlist.created_at.asc())
    )
    watchlists = result.scalars().all()

    # Gather all symbols across watchlists for batch quote lookup
    all_symbols = list({item.symbol for w in watchlists for item in w.items})
    quotes = await provider.get_quotes(all_symbols) if all_symbols else {}

    output: List[WatchlistOut] = []
    for w in watchlists:
        w_dict = {
            "id": w.id,
            "user_id": w.user_id,
            "name": w.name,
            "description": w.description,
            "is_default": w.is_default,
            "created_at": w.created_at,
            "updated_at": w.updated_at,
            "items": [
                WatchlistItemOut(
                    id=item.id,
                    watchlist_id=item.watchlist_id,
                    symbol=item.symbol,
                    custom_tag=item.custom_tag,
                    alert_preferences=item.alert_preferences or {},
                    added_at=item.added_at,
                    quote=quotes.get(item.symbol),
                )
                for item in w.items
            ],
        }
        output.append(WatchlistOut(**w_dict))
    return output


@router.post("", response_model=WatchlistOut, status_code=status.HTTP_201_CREATED)
async def create_watchlist(
    data: WatchlistCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    provider: BaseMarketDataProvider = Depends(get_market_data_provider),
):
    """Create a new watchlist."""
    # If set to default, clear previous default
    if data.is_default:
        prev_defaults = await db.execute(
            select(Watchlist).where(Watchlist.user_id == current_user.id, Watchlist.is_default == True)
        )
        for prev in prev_defaults.scalars().all():
            prev.is_default = False

    watchlist = Watchlist(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        name=data.name,
        description=data.description,
        is_default=data.is_default,
    )
    db.add(watchlist)
    await db.flush()

    # Add initial symbols if provided
    items = []
    for sym in set(data.symbols):
        item = WatchlistItem(
            id=str(uuid.uuid4()),
            watchlist_id=watchlist.id,
            symbol=sym.upper().strip(),
        )
        db.add(item)
        items.append(item)

    await db.commit()
    await db.refresh(watchlist)

    quotes = await provider.get_quotes([item.symbol for item in items]) if items else {}

    return WatchlistOut(
        id=watchlist.id,
        user_id=watchlist.user_id,
        name=watchlist.name,
        description=watchlist.description,
        is_default=watchlist.is_default,
        created_at=watchlist.created_at,
        updated_at=watchlist.updated_at,
        items=[
            WatchlistItemOut(
                id=item.id,
                watchlist_id=item.watchlist_id,
                symbol=item.symbol,
                custom_tag=item.custom_tag,
                alert_preferences=item.alert_preferences or {},
                added_at=item.added_at,
                quote=quotes.get(item.symbol),
            )
            for item in items
        ],
    )


@router.get("/{watchlist_id}", response_model=WatchlistOut)
async def get_watchlist(
    watchlist_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    provider: BaseMarketDataProvider = Depends(get_market_data_provider),
):
    """Get single watchlist details by ID with populated market quotes."""
    result = await db.execute(
        select(Watchlist)
        .where(Watchlist.id == watchlist_id, Watchlist.user_id == current_user.id)
        .options(selectinload(Watchlist.items))
    )
    watchlist = result.scalar_one_or_none()
    if not watchlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Watchlist not found")

    symbols = [item.symbol for item in watchlist.items]
    quotes = await provider.get_quotes(symbols) if symbols else {}

    return WatchlistOut(
        id=watchlist.id,
        user_id=watchlist.user_id,
        name=watchlist.name,
        description=watchlist.description,
        is_default=watchlist.is_default,
        created_at=watchlist.created_at,
        updated_at=watchlist.updated_at,
        items=[
            WatchlistItemOut(
                id=item.id,
                watchlist_id=item.watchlist_id,
                symbol=item.symbol,
                custom_tag=item.custom_tag,
                alert_preferences=item.alert_preferences or {},
                added_at=item.added_at,
                quote=quotes.get(item.symbol),
            )
            for item in watchlist.items
        ],
    )


@router.put("/{watchlist_id}", response_model=WatchlistOut)
async def update_watchlist(
    watchlist_id: str,
    data: WatchlistUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Update watchlist details."""
    result = await db.execute(
        select(Watchlist)
        .where(Watchlist.id == watchlist_id, Watchlist.user_id == current_user.id)
        .options(selectinload(Watchlist.items))
    )
    watchlist = result.scalar_one_or_none()
    if not watchlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Watchlist not found")

    if data.name is not None:
        watchlist.name = data.name
    if data.description is not None:
        watchlist.description = data.description
    if data.is_default is not None:
        if data.is_default:
            prevs = await db.execute(
                select(Watchlist).where(Watchlist.user_id == current_user.id, Watchlist.is_default == True)
            )
            for prev in prevs.scalars().all():
                prev.is_default = False
        watchlist.is_default = data.is_default

    await db.commit()
    await db.refresh(watchlist)

    return WatchlistOut(
        id=watchlist.id,
        user_id=watchlist.user_id,
        name=watchlist.name,
        description=watchlist.description,
        is_default=watchlist.is_default,
        created_at=watchlist.created_at,
        updated_at=watchlist.updated_at,
        items=[],
    )


@router.delete("/{watchlist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_watchlist(
    watchlist_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a watchlist."""
    result = await db.execute(
        select(Watchlist).where(Watchlist.id == watchlist_id, Watchlist.user_id == current_user.id)
    )
    watchlist = result.scalar_one_or_none()
    if not watchlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Watchlist not found")

    await db.delete(watchlist)
    await db.commit()


@router.post("/{watchlist_id}/items", response_model=WatchlistItemOut, status_code=status.HTTP_201_CREATED)
async def add_watchlist_item(
    watchlist_id: str,
    data: WatchlistItemCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    provider: BaseMarketDataProvider = Depends(get_market_data_provider),
):
    """Add a stock symbol to an existing watchlist."""
    # Check watchlist ownership
    result = await db.execute(
        select(Watchlist).where(Watchlist.id == watchlist_id, Watchlist.user_id == current_user.id)
    )
    watchlist = result.scalar_one_or_none()
    if not watchlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Watchlist not found")

    clean_symbol = data.symbol.strip().upper()

    # Check duplicate
    existing = await db.execute(
        select(WatchlistItem).where(
            WatchlistItem.watchlist_id == watchlist_id,
            WatchlistItem.symbol == clean_symbol,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{clean_symbol} is already in this watchlist",
        )

    item = WatchlistItem(
        id=str(uuid.uuid4()),
        watchlist_id=watchlist_id,
        symbol=clean_symbol,
        custom_tag=data.custom_tag,
        alert_preferences=data.alert_preferences,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)

    quote = await provider.get_quote(clean_symbol)

    return WatchlistItemOut(
        id=item.id,
        watchlist_id=item.watchlist_id,
        symbol=item.symbol,
        custom_tag=item.custom_tag,
        alert_preferences=item.alert_preferences or {},
        added_at=item.added_at,
        quote=quote,
    )


@router.delete("/{watchlist_id}/items/{symbol}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_watchlist_item(
    watchlist_id: str,
    symbol: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove a stock symbol from a watchlist."""
    result = await db.execute(
        select(Watchlist).where(Watchlist.id == watchlist_id, Watchlist.user_id == current_user.id)
    )
    watchlist = result.scalar_one_or_none()
    if not watchlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Watchlist not found")

    clean_symbol = symbol.strip().upper()
    item_res = await db.execute(
        select(WatchlistItem).where(
            WatchlistItem.watchlist_id == watchlist_id,
            WatchlistItem.symbol == clean_symbol,
        )
    )
    item = item_res.scalar_one_or_none()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{clean_symbol} not found in watchlist",
        )

    await db.delete(item)
    await db.commit()
