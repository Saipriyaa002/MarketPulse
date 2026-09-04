from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db
from app.core.cache import cache
from app.api.v1.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    await cache.connect()
    yield
    # Shutdown
    await cache.close()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Intelligent market watchlist backend for Code by Groww 2026",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 Router
app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for container orchestrators and monitoring."""
    return {
        "status": "ok",
        "project": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/", tags=["Health"])
async def root():
    return {
        "name": "MarketPulse API",
        "description": "Smart Market Watchlist Engine",
        "docs": "/docs",
    }
