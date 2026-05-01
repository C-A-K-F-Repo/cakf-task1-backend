"""ASGI application entrypoint."""

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings
from app.core.observability import setup_observability
from app.exceptions import register_exceptions
from app.core.redis import get_redis_client, close_redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):

    await get_redis_client()
    yield 
    await close_redis_client()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url="/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)
    register_exceptions(app)
    setup_observability(app)
    return app


app = create_app()
