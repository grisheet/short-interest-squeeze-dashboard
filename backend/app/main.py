"""FastAPI application entrypoint for the Short Interest Squeeze Dashboard."""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.database import init_db
from app.api.routes import screener, ticker, watchlist, alerts, backtests, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize DB on startup."""
    init_db()
    yield


app = FastAPI(
    title="Short Interest Squeeze Dashboard API",
    description="Production-grade API for monitoring short squeeze conditions in US equities.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(screener.router, prefix="/api", tags=["screener"])
app.include_router(ticker.router, prefix="/api", tags=["ticker"])
app.include_router(watchlist.router, prefix="/api", tags=["watchlists"])
app.include_router(alerts.router, prefix="/api", tags=["alerts"])
app.include_router(backtests.router, prefix="/api", tags=["backtests"])
app.include_router(admin.router, prefix="/api", tags=["admin"])


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"},
    )


@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}
