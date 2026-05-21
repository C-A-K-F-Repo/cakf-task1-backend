"""Top-level API router."""

from fastapi import APIRouter

from app.api.routes.acc_rec import router as acc_rec_router
from app.api.routes.auth import router as auth_router
from app.api.routes.health import router as health_router
from app.api.routes.notification import router as notification_router

api_router = APIRouter()
api_router.include_router(acc_rec_router, prefix="/account-recovery", tags=["account-recovery"])
api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(notification_router, prefix="/notify", tags=["notification"])
