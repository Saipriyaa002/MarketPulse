from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
import math
from app.providers.base import BaseMarketDataProvider
from app.schemas.market import (
    QuoteSchema,
    OHLCVSchema,
    MarketContextSchema,
    NewsItemSchema,
)

# Realistic stock catalog
MOCK_INSTRUMENTS = {
    "INFY": {
        "name": "Infosys Limited",
        "price": 1845.50,
        "previous_close": 1890.00,
        "sector": "Information Technology",
        "beta": 1.20,
        "avg_volume_20d": 5800000,
        "current_volume": 16400000,  # 2.8x surge
    },
    "TCS": {
        "name": "Tata Consultancy Services",
        "price": 4120.00,
        "previous_close": 4210.00,
        "sector": "Information Technology",
        "beta": 0.85,
        "avg_volume_20d": 2100000,
        "current_volume": 3200000,
    },
    "HDFCBANK": {
        "name": "HDFC Bank Limited",
        "price": 1685.20,
        "previous_close": 1650.00,
        "sector": "Banking & Finance",
        "beta": 1.05,
        "avg_volume_20d": 14500000,
        "current_volume": 15100000,
    },
    "ICICIBANK": {
        "name": "ICICI Bank Limited",
        "price": 1242.75,
        "previous_close": 1225.00,
        "sector": "Banking & Finance",
        "beta": 1.10,
        "avg_volume_20d": 9800000,
        "current_volume": 10200000,
    },
    "RELIANCE": {
        "name": "Reliance Industries Limited",
        "price": 2985.40,
        "previous_close": 2995.00,
        "sector": "Energy",
        "beta": 0.95,
        "avg_volume_20d": 6200000,
        "current_volume": 5900000,
    },
    "TATAMOTORS": {
        "name": "Tata Motors Limited",
        "price": 1065.80,
        "previous_close": 1020.00,
        "sector": "Automobile",
        "beta": 1.45,
        "avg_volume_20d": 8400000,
        "current_volume": 24500000,  # 2.9x surge
    },
    "MARUTI": {
        "name": "Maruti Suzuki India Limited",
        "price": 12480.00,
        "previous_close": 12510.00,
        "sector": "Automobile",
        "beta": 0.75,
        "avg_volume_20d": 450000,
        "current_volume": 420000,
    },
    "SUNPHARMA": {
        "name": "Sun Pharmaceutical Industries",
        "price": 1785.00,
        "previous_close": 1775.00,
        "sector": "Healthcare",
        "beta": 0.60,
        "avg_volume_20d": 1900000,
        "current_volume": 1850000,
    },
    "BHARTIARTL": {
        "name": "Bharti Airtel Limited",
        "price": 1580.60,
        "previous_close": 1565.00,
        "sector": "Telecom",
        "beta": 0.70,
        "avg_volume_20d": 4100000,
        "current_volume": 4300000,
    },
    "ITC": {
        "name": "ITC Limited",
        "price": 492.30,
        "previous_close": 490.50,
        "sector": "FMCG",
        "beta": 0.50,
        "avg_volume_20d": 11000000,
        "current_volume": 9800000,
    },
}

MOCK_SECTORS = {
    "Information Technology": -2.15,
    "Banking & Finance": +1.10,
    "Automobile": +2.45,
    "Energy": -0.32,
    "Healthcare": +0.55,
    "Telecom": +0.85,
    "FMCG": +0.35,
}

MOCK_NEWS = [
    {
        "id": "NEWS-INFY-01",
        "symbol": "INFY",
        "sector": "Information Technology",
        "headline": "Infosys cuts upper end of revenue growth forecast amid European spending slowdown",
        "summary": "Management cited cautious discretionary spending and delays in large deal ramp-ups during quarterly analyst call.",
        "source_name": "Reuters",
        "source_url": "https://reuters.com/business/tech/infosys-cuts-forecast",
        "event_type": "guidance",
        "sentiment_score": -0.72,
        "impact_level": "CRITICAL",
        "minutes_ago": 75,
    },
    {
        "id": "NEWS-TATA-01",
        "symbol": "TATAMOTORS",
        "sector": "Automobile",
        "headline": "Tata Motors commercial vehicle demerger gets NCLT nod; JLR margins hit 8-year peak",
        "summary": "Operating margins in the British luxury arm expanded to 9.2%, outperforming street consensus by 140 basis points.",
        "source_name": "Economic Times",
        "source_url": "https://economictimes.indiatimes.com/markets/stocks/news/tata-motors",
        "event_type": "earnings",
        "sentiment_score": 0.84,
        "impact_level": "HIGH",
        "minutes_ago": 120,
    },
    {
        "id": "NEWS-HDFC-01",
        "symbol": "HDFCBANK",
        "sector": "Banking & Finance",
        "headline": "RBI clears foreign portfolio investment weight increase for HDFC Bank",
        "summary": "MSCI August rebalancing expected to trigger estimated $1.8 billion passive institutional inflows.",
        "source_name": "Moneycontrol",
        "source_url": "https://moneycontrol.com/news/business/hdfc-bank-msci",
        "event_type": "regulatory",
        "sentiment_score": 0.65,
        "impact_level": "HIGH",
        "minutes_ago": 180,
    },
    {
        "id": "NEWS-MACRO-01",
        "symbol": None,
        "sector": "Economy",
        "headline": "India PMI Composite expands to 60.8 led by surging services demand",
        "summary": "Manufacturing output maintains robust expansion momentum while input price pressures ease.",
        "source_name": "Livemint",
        "source_url": "https://livemint.com/economy/india-pmi-growth",
        "event_type": "macro",
        "sentiment_score": 0.45,
        "impact_level": "MEDIUM",
        "minutes_ago": 240,
    },
]


class MockDataProvider(BaseMarketDataProvider):
    """
    High-fidelity deterministic mock data provider.
    Enables instant development, testing, and 100% reliable hackathon judging demos.
    """

    def __init__(self, scenario: str = "default"):
        self.scenario = scenario

    async def get_quotes(self, symbols: List[str]) -> Dict[str, QuoteSchema]:
        now = datetime.now(timezone.utc)
        result: Dict[str, QuoteSchema] = {}

        for sym in symbols:
            clean_sym = sym.upper()
            if clean_sym in MOCK_INSTRUMENTS:
                data = MOCK_INSTRUMENTS[clean_sym]
                price = data["price"]
                prev_close = data["previous_close"]
                change = round(price - prev_close, 2)
                change_pct = round((change / prev_close) * 100, 2)
                
                # Mock intraday high/low
                spread = price * 0.015
                high = round(max(price, prev_close) + spread * 0.5, 2)
                low = round(min(price, prev_close) - spread * 0.5, 2)
                open_price = round(prev_close * 1.002, 2)

                result[clean_sym] = QuoteSchema(
                    symbol=clean_sym,
                    name=data["name"],
                    price=price,
                    open=open_price,
                    high=high,
                    low=low,
                    previous_close=prev_close,
                    change=change,
                    change_pct=change_pct,
                    volume=data["current_volume"],
                    avg_volume_20d=data["avg_volume_20d"],
                    beta=data["beta"],
                    sector=data["sector"],
                    exchange="NSE",
                    timestamp=now,
                )
            else:
                # Synthetic fallback for unrecognized symbol
                base = 1000.0
                result[clean_sym] = QuoteSchema(
                    symbol=clean_sym,
                    name=f"{clean_sym} Corporation",
                    price=base,
                    open=base,
                    high=base * 1.01,
                    low=base * 0.99,
                    previous_close=base,
                    change=0.0,
                    change_pct=0.0,
                    volume=1000000,
                    avg_volume_20d=1000000,
                    beta=1.0,
                    sector="Diversified",
                    exchange="NSE",
                    timestamp=now,
                )
        return result

    async def get_market_context(self) -> MarketContextSchema:
        now = datetime.now(timezone.utc)
        return MarketContextSchema(
            benchmark_symbol="NIFTY_50",
            benchmark_name="NIFTY 50",
            benchmark_price=25180.50,
            benchmark_change=-65.20,
            benchmark_change_pct=-0.26,
            market_status="OPEN",
            sectors=MOCK_SECTORS,
            timestamp=now,
        )

    async def get_historical_ohlcv(
        self, symbol: str, lookback_days: int = 30
    ) -> List[OHLCVSchema]:
        now = datetime.now(timezone.utc)
        clean_sym = symbol.upper()
        base_price = MOCK_INSTRUMENTS.get(clean_sym, {}).get("price", 1000.0)
        
        bars: List[OHLCVSchema] = []
        for i in range(lookback_days, 0, -1):
            day_time = now - timedelta(days=i)
            # Deterministic wave oscillation
            factor = 1.0 + 0.04 * math.sin(i * 0.4) + 0.01 * math.cos(i * 0.9)
            close = round(base_price * factor, 2)
            open_p = round(close * 0.995, 2)
            high = round(max(open_p, close) * 1.012, 2)
            low = round(min(open_p, close) * 0.988, 2)
            vol = int(5000000 * (1.0 + 0.3 * math.sin(i * 0.5)))
            
            bars.append(
                OHLCVSchema(
                    timestamp=day_time,
                    open=open_p,
                    high=high,
                    low=low,
                    close=close,
                    volume=vol,
                )
            )
        return bars

    async def get_news(
        self, symbols: Optional[List[str]] = None, since: Optional[datetime] = None
    ) -> List[NewsItemSchema]:
        now = datetime.now(timezone.utc)
        items: List[NewsItemSchema] = []
        clean_symbols = [s.upper() for s in symbols] if symbols else None

        for n in MOCK_NEWS:
            published_at = now - timedelta(minutes=n["minutes_ago"])
            if since and published_at < since:
                continue

            if clean_symbols is not None and n["symbol"] is not None:
                if n["symbol"] not in clean_symbols:
                    continue

            items.append(
                NewsItemSchema(
                    id=n["id"],
                    symbol=n["symbol"],
                    sector=n["sector"],
                    headline=n["headline"],
                    summary=n["summary"],
                    source_name=n["source_name"],
                    source_url=n["source_url"],
                    event_type=n["event_type"],
                    sentiment_score=n["sentiment_score"],
                    impact_level=n["impact_level"],
                    published_at=published_at,
                )
            )
        return items

    async def search_symbols(self, query: str) -> List[Dict[str, str]]:
        q = query.strip().upper()
        results = []
        for sym, data in MOCK_INSTRUMENTS.items():
            if q in sym or q in data["name"].upper() or q in data["sector"].upper():
                results.append({
                    "symbol": sym,
                    "name": data["name"],
                    "sector": data["sector"],
                    "exchange": "NSE",
                    "price": str(data["price"]),
                })
        return results
