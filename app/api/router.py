"""Top-level API router."""

from fastapi import APIRouter

from app.api.routes.health import router as health_router
from app.api.routes.users import router as users_router
from app.api.routes.notifications import router as notifications_router
from app.api.routes.orders import router as orders_router

api_router = APIRouter()
api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(notifications_router, prefix="/notifications", tags=["notifications"])
api_router.include_router(orders_router, prefix="/orders", tags=["orders"])
