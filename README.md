# Short Interest Squeeze Dashboard

> Production-grade analytics platform for identifying and monitoring potential short squeeze conditions in US equities.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-GitHub%20Pages-blue)](https://grisheet.github.io/short-interest-squeeze-dashboard/)
[![Python](https://img.shields.io/badge/Python-3.11+-green)](https://python.org)
[![React](https://img.shields.io/badge/React-18+-61DAFB)](https://reactjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue)](https://typescriptlang.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Overview

The Short Interest Squeeze Dashboard combines FINRA-delayed exchange-reported short interest with more timely securities lending data, price/volume signals, and options-derived indicators to help traders identify potential squeeze setups.

The system clearly labels FINRA-reported short interest as **stale/twice-monthly** while borrow cost, utilization, volume, and options activity provide more current pressure signals.

---

## Live Demo

**[View the live dashboard on GitHub Pages](https://grisheet.github.io/short-interest-squeeze-dashboard/)**

The GitHub Pages deployment serves the React frontend with deterministic mock data that simulates 18 months of real market conditions, including engineered squeeze episodes for GME-like and BBBY-like scenarios.

---

## Features

### Dashboard
- **KPI Bar**: Total screened tickers, high-conviction squeeze candidates, avg borrow cost, avg utilization
- **Squeeze Pressure Trends**: 30-day rolling chart of avg squeeze score across watchlist
- **Top Movers**: Short interest change leaders over configurable period
- **Screener Table**: Sortable, filterable table with all key metrics
- **Ticker Detail Page**: Full single-ticker deep-dive with history, options chain, narrative, and squeeze episodes

### Analytics Engine
| Metric | Source | Freshness |
|--------|--------|-----------|
| Short Interest Shares | FINRA | ~2x/month (stale) |
| Short Interest % Float | FINRA | ~2x/month (stale) |
| Days to Cover (DTC) | Calc: SI / ADV | ~2x/month |
| Securities on Loan | Securities lending | Near-realtime |
| Cost to Borrow | Securities lending | Near-realtime |
| Utilization | Securities lending | Near-realtime |
| Borrow Fee | Securities lending | Near-realtime |
| Options OI by Strike | Options chain | Daily |
| Put/Call Ratio | Options chain | Daily |
| Gamma Exposure | Dealer model | Daily |
| Squeeze Score (0-100) | ML + Rules | Daily |

### Squeeze Scoring
- **Rule-based signals**: High borrow fees, extreme utilization, rising SI%, low DTC
- **ML model**: Logistic regression + gradient boosting ensemble trained on labeled historical squeezes
- **Backtest service**: Compares rule-based vs ML ranking on historical data

### Architecture
- Modular **Provider interface** — swap between mock, Ortex, Fintel, or any data vendor via config
- **ETL jobs** ingest data, compute aggregates and scores, and flag freshness
- **Notification system** for squeeze alert delivery
- **Background scheduler** for automated data refresh

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18 + TypeScript 5, Recharts, Tailwind CSS |
| Backend | Python 3.11, FastAPI 0.104 |
| Database | PostgreSQL 15 (SQLite for dev) |
| ORM | SQLAlchemy 2.0 |
| ML | scikit-learn (LogisticRegression + GradientBoosting) |
| Jobs | APScheduler (Celery-compatible interface) |
| Caching | Redis (optional) |
| Auth | JWT — analyst/admin roles |
| Containers | Docker + docker-compose |
| CI/CD | GitHub Actions |
| Hosting | GitHub Pages (frontend) |

---

## Project Structure

```
short-interest-squeeze-dashboard/
├── backend/
│   └── app/
│       ├── api/
│       │   └── routes/
│       │       ├── screener.py      # GET /api/screener
│       │       ├── ticker.py        # GET /api/ticker/{symbol}/*
│       │       ├── watchlist.py     # Watchlist CRUD
│       │       ├── alerts.py        # Alert management
│       │       ├── backtests.py     # Backtest endpoints
│       │       └── admin.py         # Admin / data quality
│       ├── core/
│       │   ├── config.py            # Settings & env management
│       │   ├── database.py          # SQLAlchemy engine/session
│       │   └── auth.py              # JWT auth dependency
│       ├── models/
│       │   └── models.py            # SQLAlchemy ORM models
│       ├── schemas/
│       │   └── schemas.py           # Pydantic request/response schemas
│       ├── providers/
│       │   ├── base.py              # Abstract provider interfaces
│       │   ├── mock_data.py         # Deterministic mock data engine
│       │   ├── mock_adapters.py     # Mock provider adapters
│       │   └── registry.py         # Provider registry (config-driven)
│       ├── services/
│       │   ├── squeeze_score.py     # Core squeeze scoring logic
│       │   ├── metrics.py           # Point-in-time signal computation
│       │   ├── screener.py          # Screener service
│       │   ├── ticker.py            # Ticker detail service
│       │   ├── ml_pipeline.py       # Feature engineering + ML models
│       │   ├── backtest.py          # Backtest service
│       │   ├── etl.py               # ETL jobs
│       │   ├── notifications.py     # Alert delivery
│       │   └── scheduler.py         # Background scheduler
│       └── main.py                  # FastAPI app entrypoint
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   └── Header.tsx
│   │   │   ├── dashboard/
│   │   │   │   ├── KPIBar.tsx
│   │   │   │   ├── SqueezeTrendChart.tsx
│   │   │   │   ├── TopMovers.tsx
│   │   │   │   └── ScreenerTable.tsx
│   │   │   ├── ticker/
│   │   │   │   ├── TickerOverview.tsx
│   │   │   │   ├── HistoryChart.tsx
│   │   │   │   ├── OptionsChain.tsx
│   │   │   │   └── SqueezeNarrative.tsx
│   │   │   └── ui/
│   │   │       ├── Badge.tsx
│   │   │       ├── DataTable.tsx
│   │   │       └── MetricCard.tsx
│   │   ├── data/
│   │   │   └── mockData.ts          # Static mock data for GitHub Pages
│   │   ├── hooks/
│   │   │   ├── useScreener.ts
│   │   │   └── useTicker.ts
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   └── TickerDetail.tsx
│   │   ├── types/
│   │   │   └── index.ts
│   │   ├── utils/
│   │   │   └── formatters.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── scripts/
│   └── seed_db.py                   # Seed script: 18 months mock data
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

---

## Quick Start

### Prerequisites
- Docker & docker-compose
- Node.js 18+
- Python 3.11+

### 1. Clone the repo
```bash
git clone https://github.com/grisheet/short-interest-squeeze-dashboard.git
cd short-interest-squeeze-dashboard
```

### 2. Configure environment
```bash
cp .env.example .env
# Edit .env — defaults work out of the box with SQLite and mock providers
```

### 3. Start with Docker
```bash
docker-compose up --build
```

This starts:
- **FastAPI backend** at `http://localhost:8000`
- **PostgreSQL** at `localhost:5432`
- **Redis** at `localhost:6379`

### 4. Seed the database
```bash
docker-compose exec backend python scripts/seed_db.py
```

### 5. Start the frontend
```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`

### 6. API docs
FastAPI interactive docs: `http://localhost:8000/docs`

---

## Data Providers

The provider system uses a registry pattern — swap vendors via `DATA_PROVIDER` env var:

```env
# .env
DATA_PROVIDER=mock          # deterministic mock (default)
DATA_PROVIDER=ortex         # Ortex API (requires API key)
DATA_PROVIDER=fintel        # Fintel API (requires API key)
```

All providers implement the same abstract interfaces in `backend/app/providers/base.py`.

---

## Squeeze Score Methodology

The squeeze score (0-100) combines:

| Component | Weight | Rationale |
|-----------|--------|-----------|
| Borrow cost | 25% | High fees = forced covering pressure |
| Utilization | 20% | Near 100% = no more shares to short |
| Short % Float | 20% | High float SI = fuel for squeeze |
| Days to Cover | 15% | Lower DTC = faster potential squeeze |
| Volume spike | 10% | Unusual volume = early buying pressure |
| Options gamma | 10% | Dealer hedging amplifies price moves |

ML model adds precision: trained on 18 months of mock data with labeled squeeze episodes, uses logistic regression + gradient boosting ensemble.

---

## API Reference

### Screener
```
GET /api/screener?min_score=60&sort_by=squeeze_score&limit=50
```

### Ticker Detail
```
GET /api/ticker/{symbol}/overview
GET /api/ticker/{symbol}/history?days=90
GET /api/ticker/{symbol}/options
GET /api/ticker/{symbol}/narrative
GET /api/ticker/{symbol}/episodes
```

### Watchlists & Alerts
```
GET/POST/DELETE /api/watchlists
GET/POST/DELETE /api/alerts
```

### Backtests
```
POST /api/backtests/run
GET  /api/backtests/{id}/results
```

### Admin
```
GET  /api/admin/data-quality
POST /api/admin/refresh
GET  /api/admin/model/metrics
```

Full interactive docs at `/docs` (Swagger UI) or `/redoc`.

---

## Development

### Running tests
```bash
cd backend
pip install -r requirements.txt
pytest tests/ -v
```

### Linting
```bash
# Backend
ruff check backend/
mypy backend/

# Frontend
cd frontend && npm run lint
```

### Building for production
```bash
cd frontend
npm run build
# Output in frontend/dist/ — deployed to GitHub Pages via Actions
```

---

## GitHub Pages Deployment

The frontend is automatically deployed to GitHub Pages on every push to `main`.

The GitHub Pages build uses the static mock data in `frontend/src/data/mockData.ts` — no backend required for the demo.

To deploy manually:
```bash
cd frontend
npm run build
npm run deploy
```

---

## Configuration Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./squeeze.db` | Database connection string |
| `DATA_PROVIDER` | `mock` | Data vendor: mock/ortex/fintel |
| `REDIS_URL` | `redis://localhost:6379` | Redis URL (optional) |
| `JWT_SECRET` | `changeme` | JWT signing secret |
| `FINRA_DATA_DIR` | `./data/finra` | Local FINRA CSV directory |
| `ALERT_EMAIL_SMTP` | — | SMTP host for email alerts |
| `SCHEDULER_INTERVAL_HOURS` | `6` | ETL refresh interval |

---

## License

MIT License — see [LICENSE](LICENSE)

---

## Disclaimer

This tool is for **informational and educational purposes only**. It does not constitute financial advice. Short selling and squeeze trading involve substantial risk of loss. Always conduct your own research and consult a qualified financial advisor before making investment decisions.
