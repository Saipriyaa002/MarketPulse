# MarketPulse Backend

FastAPI backend for **MarketPulse**, an intelligent market watchlist built for the **CODE by Groww 2026** hackathon.

The backend handles market data, watchlists, checkpoints, change detection, attention scoring, event correlation, and grounded AI explanations.

## Tech Stack

* **FastAPI** — REST API
* **Python**
* **SQLAlchemy** — database access
* **SQLite / PostgreSQL** — persistence
* **Redis / In-memory cache** — caching
* **Deterministic market analysis** — calculations and scoring
* **AI explanation layer** — explains validated facts without generating market data

## Project Structure

```text
backend/
├── app/
│   ├── api/          # API routes
│   ├── core/         # Configuration and core utilities
│   ├── models/       # Database models
│   ├── providers/    # Market data providers
│   ├── schemas/      # API schemas
│   └── services/     # Business logic
├── tests/             # Backend test suite
├── requirements.txt
└── README.md
```

## Running Locally

Create and activate a Python virtual environment, install dependencies, and run:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

The project uses SQLite by default for simple local development and a mock market provider for reliable demonstrations.

## Testing

Run the complete backend test suite:

```bash
pytest -v
```

The tests cover authentication, watchlists, checkpoints, market data, change detection, attention scoring, event correlation, and AI fallback behavior.

## Design Principle

Market facts are calculated **deterministically by the backend**. AI is used only to explain validated results through a facts dossier, with a deterministic fallback when an LLM is unavailable.

This keeps MarketPulse reliable, explainable, and suitable for the hackathon demo.
