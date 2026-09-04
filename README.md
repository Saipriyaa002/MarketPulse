# MarketPulse

### Smart Market Watchlist — CODE by Groww 2026

MarketPulse is an intelligent market watchlist that helps users understand **what meaningfully changed since they last checked** and **what deserves their attention now**.

Unlike a traditional watchlist that mainly displays prices and percentage changes, MarketPulse compares the current market state with a user's previous checkpoint and identifies meaningful movements using market-relative performance, sector divergence, volume anomalies, and relevant events.

---

## Problem

A normal stock watchlist can tell you:

* Current price
* Daily percentage change
* Trading volume

But it doesn't answer:

> **"What changed since the last time I checked, and is it actually important?"**

MarketPulse solves this by maintaining a personalized checkpoint for the user and analyzing changes from that point onward.

---

## Key Features

* Create and manage stock watchlists
* Persistent user checkpoints
* "Since You Last Checked" analysis
* Market-relative alpha using beta-adjusted returns
* Sector divergence detection
* Volume anomaly detection using Z-scores
* Attention Score for prioritizing important stocks
* Correlated market events and news
* Evidence and confidence indicators
* Grounded AI explanations
* Deterministic fallback when AI is unavailable
* "Catch Me Up" checkpoint reset
* 2-hour, 4-hour and 24-hour Time Leap demo
* Watchlist-level "What Did I Miss?" digest
* Guest/Demo Mode for quick evaluation

---

## How It Works

```text
User opens watchlist
        ↓
Latest market state is retrieved
        ↓
Previous checkpoint is loaded
        ↓
Current state is compared with checkpoint
        ↓
Meaningful changes are detected
        ↓
Attention scores are calculated
        ↓
Relevant evidence and events are attached
        ↓
AI explains the validated findings
```

The core idea is **checkpoint-based change detection**, rather than simply showing standard daily market changes.

---

## Architecture

MarketPulse uses a **modular monolith** architecture.

```text
                 Next.js Frontend
                       │
                       ▼
                  FastAPI API
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
       Auth        Watchlists   Market Data
                                    │
                           ┌────────┼────────┐
                           ▼        ▼        ▼
                       Change   Attention  Events
                      Detection  Scoring  Correlation
                           │
                           ▼
                     Facts Dossier
                           │
                           ▼
                      AI Explainer
```

### Technology Stack

**Frontend**

* Next.js
* TypeScript
* Tailwind CSS
* Recharts

**Backend**

* Python
* FastAPI
* SQLAlchemy
* Pydantic
* Pytest

**Database & Cache**

* PostgreSQL / SQLite
* Redis with in-memory fallback

**Market Data**

* Mock market provider for reliable demonstrations
* yfinance provider support

**AI**

* Gemini / OpenAI / Groq
* Deterministic fallback explanation

---

## AI Approach

MarketPulse follows a **deterministic-first architecture**.

The AI does not calculate or invent financial information.

The backend first calculates validated facts such as:

* Price change
* Market-relative alpha
* Sector divergence
* Volume anomaly
* Attention score
* Relevant events

These are passed to the AI as a structured **Facts Dossier**.

The AI's role is to explain the existing evidence in a concise and understandable way.

If the AI service is unavailable, the system automatically falls back to deterministic explanations.

---

## Demo

MarketPulse includes a Time Leap simulation so the core functionality can be demonstrated even when live markets are closed.

### Recommended Demo Flow

1. Enter **Guest Demo Mode**
2. View the default watchlist
3. Click **Simulate 4 Hours Ago**
4. Observe meaningful changes in the watchlist
5. Open the highest-attention stock
6. Inspect quantitative evidence
7. Review correlated events/news
8. Generate the AI Deep-Dive
9. Click **Catch Me Up**
10. The current state becomes the new checkpoint

---

## Running Locally

### Backend

```bash
cd backend
python -m venv venv
```

Windows:

```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Start the API:

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

API: `http://127.0.0.1:8000`

Swagger documentation: `http://127.0.0.1:8000/docs`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Application: `http://localhost:3000`

---

## Testing

Backend tests:

```bash
cd backend
pytest -v
```

Frontend production build:

```bash
cd frontend
npm run build
```

The project includes tests covering authentication, watchlists, market providers, change detection, attention scoring, event correlation, AI fallback, checkpoints, and API flows.

---

## Project Structure

```text
MarketPulse/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── providers/
│   │   ├── schemas/
│   │   └── services/
│   └── tests/
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── lib/
│   │   └── types/
│   └── public/
│
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Engineering Principles

MarketPulse prioritizes:

**Correctness → Reliability → Clarity → Polish → Extra Features**

The project intentionally avoids unnecessary complexity such as trading execution, social feeds, microservices, Kafka/RabbitMQ, Kubernetes, or custom ML model training.

The goal is simple:

> **Don't just show users what the market is doing. Show them what meaningfully changed, why it changed, and why it deserves their attention.**
