# MarketPulse Frontend

Frontend for **MarketPulse**, an intelligent market watchlist built for the **CODE by Groww 2026** hackathon.

The interface helps users quickly understand **what changed since their last check and what deserves their attention**.

## Tech Stack

* **Next.js 14** — React framework
* **TypeScript**
* **Tailwind CSS**
* **Recharts** — data visualization
* **Lucide React** — UI icons

## Features

* Watchlist dashboard with market context
* "Since you last checked" intelligence briefing
* Attention-based stock ranking
* Market-relative alpha and sector divergence
* Volume anomaly indicators
* Stock detail and evidence drawer
* Correlated news and catalysts
* Grounded AI explanations
* Catch Me Up checkpoint flow
* Time Leap demo mode
* Guest/demo experience

## Project Structure

```text
frontend/
├── src/
│   ├── app/          # Next.js pages and routes
│   ├── components/   # UI components
│   ├── hooks/        # React hooks
│   ├── lib/          # API and utility functions
│   └── types/        # TypeScript types
├── public/            # Static assets
├── package.json
└── package-lock.json
```

## Running Locally

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

The application will be available at:

```text
http://localhost:3000
```

Build for production:

```bash
npm run build
```

The frontend communicates with the FastAPI backend to retrieve watchlist, market, checkpoint, and intelligence data.

## Design Principle

The UI prioritizes **clarity over information overload** — showing what changed, how unusual the movement is, why it matters, and the evidence supporting it.
