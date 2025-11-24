"""
API Router Aggregator
Centralized router management to keep main.py clean
"""
from fastapi import APIRouter

from .album import router as album_router
from .item import router as item_router
from .song import router as song_router
from .team import router as team_router
from .user import router as user_router
from .product import router as product_router

# Create a main API router that includes all sub-routers with /api/v1/ prefix
api_router = APIRouter(prefix="/api/v1")

# Include all API routers
api_router.include_router(album_router)
api_router.include_router(item_router)
api_router.include_router(song_router)
api_router.include_router(team_router)
api_router.include_router(user_router)
api_router.include_router(product_router)

# Export for easy import
__all__ = ["api_router"]
