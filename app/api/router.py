"""Top-level API router."""

from fastapi import APIRouter

from app.api.routes.acc_rec import router as acc_rec_router
from app.api.routes.auth import router as auth_router
from app.api.routes.health import router as health_router
from app.api.routes.orders import router as orders_router
from app.api.routes.products import router as products_router
from app.api.routes.product_types import router as product_types_router

api_router = APIRouter()
api_router.include_router(acc_rec_router, prefix="/account-recovery", tags=["account-recovery"])
api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(orders_router, prefix="/orders", tags=["orders"])
api_router.include_router(products_router, prefix="/products", tags=["products"])
api_router.include_router(product_types_router, prefix="/product-types", tags=["product-types"])
