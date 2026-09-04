# MarketPulse - Smart Market Watchlist

> Intelligent market watchlist built for **Code by Groww 2026**.
> Core feature: *"Since you last checked"* — remembers what the user last saw, detects meaningful relative changes, correlates market/sector context, ranks movements by attention level, and explains findings with deterministic-first, evidence-backed AI.

---

## Tech Stack

- **Frontend**: Next.js, React, TypeScript, Tailwind CSS, Recharts, Lucide Icons
- **Backend**: Python 3.11+, FastAPI, SQLAlchemy 2.0 (async), Pydantic v2
- **Database**: PostgreSQL (with automatic zero-config SQLite async fallback for local dev)
- **Cache**: Redis (with automatic in-memory TTL fallback)
- **Market Data**: `BaseMarketDataProvider` abstraction with `MockDataProvider` (realistic Indian equity universe) + live provider capabilities

---

## Quickstart

### Backend Setup

```bash
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# Run test suite
$env:PYTHONPATH="."
.\venv\Scripts\pytest -v

# Start FastAPI server
uvicorn app.main:app --reload --port 8000
```

Interactive API documentation will be available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Health check: `http://localhost:8000/health`

---

## Docker Setup (Optional)

To run PostgreSQL and Redis in Docker containers:

```bash
docker-compose up -d
```
