from fastapi import APIRouter
from app.api.v1 import auth, watchlists, market, checkpoints, pulse

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(watchlists.router, prefix="/watchlists", tags=["Watchlists"])
api_router.include_router(market.router, prefix="/market", tags=["Market Data"])
api_router.include_router(checkpoints.router, prefix="/checkpoints", tags=["Checkpoints"])
api_router.include_router(pulse.router, prefix="/pulse", tags=["Market Pulse"])
