from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.models.user import User
from app.models.watchlist import Watchlist
from app.models.checkpoint import UserCheckpoint
from app.schemas.pulse import PulseItemSchema, PulseResponseSchema
from app.services.checkpoint import CheckpointService
from app.services.change_detection import ChangeDetectionEngine
from app.services.attention_scorer import AttentionScorer
from app.services.ai_explainer import AIExplainerService
from app.api.deps import get_current_active_user, get_market_data_provider
from app.providers.base import BaseMarketDataProvider
from app.api.v1.checkpoints import format_human_elapsed

router = APIRouter()


class TimeLeapRequest(BaseModel):
    watchlist_id: str
    hours_ago: float = Field(4.0, ge=0.1, le=168.0, description="Hours back in time to simulate")
    simulate_volatility: bool = Field(True, description="Artificially vary baseline prices for realistic demonstration")


@router.get("/since-last-seen", response_model=PulseResponseSchema)
async def get_since_last_seen(
    watchlist_id: str = Query(..., description="ID of the watchlist to analyze"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    provider: BaseMarketDataProvider = Depends(get_market_data_provider),
):
    """
    Core intelligent feature of MarketPulse.
    Calculates what meaningfully changed strictly since the user last checked:
    - Market benchmark return over delta window
    - Sector return over delta window
    - Stock return over delta window
    - Beta-adjusted excess return (Alpha)
    - Sector divergence
    - Volume anomaly (Z-Score)
    - Attention score ranking (0-100)
    - Defensible Evidence Confidence
    """
    # 1. Fetch watchlist
    wl_res = await db.execute(
        select(Watchlist)
        .where(Watchlist.id == watchlist_id, Watchlist.user_id == current_user.id)
        .options(selectinload(Watchlist.items))
    )
    watchlist = wl_res.scalar_one_or_none()
    if not watchlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Watchlist not found")

    if not watchlist.items:
        # Empty watchlist handling
        now = datetime.now(timezone.utc)
        return PulseResponseSchema(
            watchlist_id=watchlist.id,
            watchlist_name=watchlist.name,
            checkpoint_id="none",
            checkpoint_time=now,
            elapsed_seconds=0,
            human_elapsed="never",
            benchmark_status={"name": "Nifty 50", "change_pct": 0.0},
            total_items=0,
            meaningful_count=0,
            critical_count=0,
            executive_summary="Your watchlist is currently empty. Add stocks to start receiving intelligent market pulse alerts.",
            items=[],
        )

    # 2. Get active checkpoint
    checkpoint = await CheckpointService.get_or_create_latest_checkpoint(
        db, current_user.id, watchlist.id, provider
    )
    cp_time = checkpoint.checkpoint_time.replace(tzinfo=timezone.utc) if checkpoint.checkpoint_time.tzinfo is None else checkpoint.checkpoint_time
    now = datetime.now(timezone.utc)
    elapsed_seconds = max(0, int((now - cp_time).total_seconds()))
    human_elapsed = format_human_elapsed(elapsed_seconds)

    snapshot_items = checkpoint.snapshot_data.get("items", {})
    cp_benchmark = checkpoint.snapshot_data.get("benchmark", {})
    cp_sectors = checkpoint.snapshot_data.get("sectors", {})

    # 3. Fetch current live market data & context
    symbols = [item.symbol for item in watchlist.items]
    quotes = await provider.get_quotes(symbols)
    context = await provider.get_market_context()
    recent_news = await provider.get_news(symbols=symbols, since=cp_time - timedelta(hours=2))

    # Calculate Benchmark delta SINCE CHECKPOINT
    curr_bm_price = context.benchmark_price
    cp_bm_price = cp_benchmark.get("price", curr_bm_price) if cp_benchmark else curr_bm_price
    if cp_bm_price and cp_bm_price > 0 and abs(curr_bm_price - cp_bm_price) > 0.01:
        benchmark_delta_pct = round(((curr_bm_price - cp_bm_price) / cp_bm_price) * 100, 2)
    else:
        benchmark_delta_pct = 0.0

    # Map news by symbol
    news_by_symbol: Dict[str, list] = {}
    for n in recent_news:
        if n.symbol:
            news_by_symbol.setdefault(n.symbol.upper(), []).append(n)

    # 4. Evaluate each stock through Change Detection & Attention Scoring
    pulse_items: List[PulseItemSchema] = []

    for sym in symbols:
        quote = quotes.get(sym)
        if not quote:
            continue

        cp_item = snapshot_items.get(sym)
        
        # Sector delta SINCE CHECKPOINT
        curr_sec_val = context.sectors.get(quote.sector, 0.0)
        cp_sec_val = cp_sectors.get(quote.sector, curr_sec_val) if cp_sectors else curr_sec_val
        sector_delta_pct = round(curr_sec_val - cp_sec_val, 2)

        # Meaningful-change engine
        change_result = ChangeDetectionEngine.evaluate_stock_change(
            quote=quote,
            checkpoint_item=cp_item,
            benchmark_change_pct=benchmark_delta_pct,
            sector_change_pct=sector_delta_pct,
        )

        # Attention scorer
        sym_news = news_by_symbol.get(sym, [])
        attention = AttentionScorer.calculate_attention(
            change=change_result,
            related_news=sym_news,
            data_freshness_seconds=15,
            has_checkpoint_baseline=(cp_item is not None),
        )

        pulse_items.append(
            PulseItemSchema(
                symbol=change_result.symbol,
                name=change_result.name,
                sector=change_result.sector_name,
                current_price=change_result.current_price,
                checkpoint_price=change_result.checkpoint_price,
                price_change=change_result.price_change,
                price_change_pct=change_result.price_change_pct,
                session_change_pct=change_result.session_change_pct,
                alpha_excess_pct=change_result.alpha_excess_pct,
                sector_divergence_pct=change_result.sector_divergence_pct,
                volume_z_score=change_result.volume_z_score,
                current_volume=change_result.current_volume,
                avg_volume_20d=change_result.avg_volume_20d,
                attention_score=attention["score"],
                attention_level=attention["level"],
                confidence_score=attention["confidence_score"],
                confidence_tier=attention["confidence_tier"],
                confidence_tier_description=attention["confidence_tier_description"],
                confidence_breakdown=attention["confidence_breakdown"],
                is_meaningful=change_result.is_meaningful,
                primary_drivers=change_result.primary_drivers,
                summary=attention["deterministic_summary"],
                breakdown=attention["breakdown"],
                related_events=attention["related_events"],
            )
        )

    # 5. Rank by Attention Score (highest urgency first)
    pulse_items.sort(key=lambda x: x.attention_score, reverse=True)

    # 6. Synthesize executive summary
    total_count = len(pulse_items)
    meaningful_count = sum(1 for x in pulse_items if x.is_meaningful)
    critical_count = sum(1 for x in pulse_items if x.attention_level == "CRITICAL")

    if critical_count > 0:
        top_stock = pulse_items[0]
        exec_summary = (
            f"Since you last checked ({human_elapsed}): {meaningful_count} of {total_count} stocks exhibited meaningful divergence. "
            f"Urgent attention required on {top_stock.symbol} ({top_stock.price_change_pct:+.2f}%, Attention Score: {top_stock.attention_score}/100) "
            f"due to {', '.join(top_stock.primary_drivers[:2])}."
        )
    elif meaningful_count > 0:
        top_stock = pulse_items[0]
        exec_summary = (
            f"Since you last checked ({human_elapsed}): {meaningful_count} of {total_count} stocks moved beyond expected market beta, "
            f"led by {top_stock.symbol} ({top_stock.price_change_pct:+.2f}%)."
        )
    else:
        if elapsed_seconds < 90:
            exec_summary = (
                f"You're all caught up! Watchlist checkpoint established {human_elapsed}. "
                f"All {total_count} stocks are at baseline. New market-relative shifts will appear as trading progresses."
            )
        else:
            exec_summary = (
                f"Since you last checked ({human_elapsed}): All {total_count} stocks are trading within normal expected market variance. "
                f"No critical anomalies or sector divergences detected."
            )

    return PulseResponseSchema(
        watchlist_id=watchlist.id,
        watchlist_name=watchlist.name,
        checkpoint_id=checkpoint.id,
        checkpoint_time=cp_time,
        elapsed_seconds=elapsed_seconds,
        human_elapsed=human_elapsed,
        benchmark_status={
            "symbol": context.benchmark_symbol,
            "name": context.benchmark_name,
            "price": context.benchmark_price,
            "change_pct": benchmark_delta_pct,
            "session_change_pct": context.benchmark_change_pct,
            "status": context.market_status,
        },
        total_items=total_count,
        meaningful_count=meaningful_count,
        critical_count=critical_count,
        executive_summary=exec_summary,
        items=pulse_items,
    )


@router.post("/simulate-time-leap", response_model=PulseResponseSchema)
async def simulate_time_leap(
    data: TimeLeapRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    provider: BaseMarketDataProvider = Depends(get_market_data_provider),
):
    """
    Demo Layer: Simulates a time leap into the past so judges can immediately observe
    what changed 'Since you last checked 4 hours ago' with realistic volatility deltas.
    """
    # 1. Fetch watchlist
    wl_res = await db.execute(
        select(Watchlist)
        .where(Watchlist.id == data.watchlist_id, Watchlist.user_id == current_user.id)
        .options(selectinload(Watchlist.items))
    )
    watchlist = wl_res.scalar_one_or_none()
    if not watchlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Watchlist not found")

    # 2. Build synthetic past snapshot
    past_time = datetime.now(timezone.utc) - timedelta(hours=data.hours_ago)
    symbols = [item.symbol for item in watchlist.items]
    quotes = await provider.get_quotes(symbols)
    context = await provider.get_market_context()

    # Timeframe-scaled drift factors
    if data.hours_ago >= 20:
        # 24h gap (yesterday close)
        bm_factor = 1.004
        sec_offsets = {
            "Information Technology": 1.20,
            "Automobile": -2.80,
            "Banking & Finance": -1.20,
            "Energy": 0.20,
            "Healthcare": -0.40,
            "Telecom": -0.60,
            "FMCG": -0.30,
        }
        drift_factors = {
            "INFY": 1.048,
            "TATAMOTORS": 0.938,
            "HDFCBANK": 0.975,
            "TCS": 1.031,
            "RELIANCE": 1.008,
            "MARUTI": 0.985,
            "SUNPHARMA": 0.990,
            "BHARTIARTL": 0.988,
            "ITC": 0.995,
        }
    elif data.hours_ago >= 3.5:
        # 4 hours ago (recommended hackathon demo)
        bm_factor = 1.003
        sec_offsets = {
            "Information Technology": 0.60,
            "Automobile": -1.50,
            "Banking & Finance": -0.50,
            "Energy": 0.10,
            "Healthcare": -0.20,
            "Telecom": -0.30,
            "FMCG": -0.10,
        }
        drift_factors = {
            "INFY": 1.035,        # 4h ago was 3.5% higher (now dropped -3.38%)
            "TATAMOTORS": 0.955,  # 4h ago was 4.5% lower (now surged +4.71%)
            "HDFCBANK": 0.985,    # 4h ago was 1.5% lower (now up +1.52%)
            "TCS": 1.020,         # 4h ago was 2.0% higher (now down -1.96%)
            "RELIANCE": 1.002,    # Flat
            "MARUTI": 0.990,
            "SUNPHARMA": 0.995,
            "BHARTIARTL": 0.992,
            "ITC": 0.998,
        }
    else:
        # 2 hours ago
        bm_factor = 1.0015
        sec_offsets = {
            "Information Technology": 0.30,
            "Automobile": -0.75,
            "Banking & Finance": -0.25,
            "Energy": 0.05,
            "Healthcare": -0.10,
            "Telecom": -0.15,
            "FMCG": -0.05,
        }
        drift_factors = {
            "INFY": 1.018,
            "TATAMOTORS": 0.978,
            "HDFCBANK": 0.992,
            "TCS": 1.010,
            "RELIANCE": 1.001,
            "MARUTI": 0.995,
            "SUNPHARMA": 0.998,
            "BHARTIARTL": 0.996,
            "ITC": 0.999,
        }

    # Synthetic benchmark at checkpoint
    past_bm_price = round(context.benchmark_price * bm_factor, 2) if data.simulate_volatility else context.benchmark_price

    # Synthetic sectors at checkpoint
    past_sectors = {}
    for sec, curr_val in context.sectors.items():
        offset = sec_offsets.get(sec, 0.0) if data.simulate_volatility else 0.0
        past_sectors[sec] = round(curr_val + offset, 2)

    synthetic_snapshot: Dict[str, Any] = {
        "captured_at": past_time.isoformat(),
        "benchmark": {
            "symbol": context.benchmark_symbol,
            "price": past_bm_price,
            "change_pct": 0.0,
        },
        "sectors": past_sectors,
        "items": {},
    }

    for sym, q in quotes.items():
        factor = drift_factors.get(sym, 1.0) if data.simulate_volatility else 1.0
        past_price = round(q.price * factor, 2)
        synthetic_snapshot["items"][sym] = {
            "symbol": q.symbol,
            "name": q.name,
            "price": past_price,
            "change_pct": 0.0,
            "volume": int(q.volume * 0.4),
            "avg_volume_20d": q.avg_volume_20d,
            "beta": q.beta,
            "sector": q.sector,
            "timestamp": past_time.isoformat(),
        }

    # 3. Clean up any previous demo checkpoints to avoid state pollution
    await db.execute(
        delete(UserCheckpoint).where(
            UserCheckpoint.user_id == current_user.id,
            UserCheckpoint.watchlist_id == watchlist.id,
            UserCheckpoint.trigger_event == "time_leap_demo",
        )
    )

    checkpoint = UserCheckpoint(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        watchlist_id=watchlist.id,
        device_id="demo-simulator",
        checkpoint_time=past_time,
        snapshot_data=synthetic_snapshot,
        trigger_event="time_leap_demo",
    )
    db.add(checkpoint)
    await db.commit()

    # 4. Return updated pulse feed
    return await get_since_last_seen(
        watchlist_id=data.watchlist_id,
        current_user=current_user,
        db=db,
        provider=provider,
    )


@router.get("/explain/{symbol}")
async def explain_symbol(
    symbol: str,
    watchlist_id: str = Query(..., description="ID of the watchlist"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    provider: BaseMarketDataProvider = Depends(get_market_data_provider),
):
    """
    On-demand grounded AI explanation for a single stock movement.
    Provides structured executive takeaways, risk assessment, and fact confidence.
    """
    pulse = await get_since_last_seen(watchlist_id, current_user, db, provider)
    target_item = next((item for item in pulse.items if item.symbol == symbol.upper().strip()), None)
    if not target_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Symbol '{symbol}' not found in watchlist pulse feed",
        )

    return await AIExplainerService.explain_stock(
        item=target_item,
        checkpoint_time=pulse.checkpoint_time.isoformat(),
    )


@router.get("/digest")
async def get_watchlist_digest(
    watchlist_id: str = Query(..., description="ID of the watchlist"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    provider: BaseMarketDataProvider = Depends(get_market_data_provider),
):
    """
    'What Did I Miss?' - Executive Watchlist Digest.
    Summarizes macro environment, critical alerts, and sector decoupling across the portfolio.
    """
    pulse = await get_since_last_seen(watchlist_id, current_user, db, provider)
    return AIExplainerService.generate_watchlist_digest(pulse)
