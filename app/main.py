"""ASGI application entrypoint."""

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.observability import setup_observability
from app.exceptions import register_exceptions
from app.core.redis import get_redis_client, close_redis_client
from app.core.db import SessionLocal
from app.tasks.birthday import notify_birthday
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler


@asynccontextmanager
async def lifespan(_app: FastAPI):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(notify_birthday, 'cron', hour=9, minute=0)
    scheduler.start()
    yield
    scheduler.shutdown()
    await close_redis_client()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url="/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.FRONTEND_URL],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)
    register_exceptions(app)
    setup_observability(app)
    return app


app = create_app()
