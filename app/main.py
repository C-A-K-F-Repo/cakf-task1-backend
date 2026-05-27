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
from fastapi.staticfiles import StaticFiles


async def seed_admin() -> None:
    """Ensure a default administrator exists for first login."""
    from app.core.personal_data_crypto import lookup_hash, normalize_email
    from app.core.security import password_hash
    from app.models.user import User
    from app.repositories.user import UserRepository
    from app.models.roles import Role

    async with SessionLocal() as db:
        repo = UserRepository(db)
        if await repo.get_by_email(settings.ADMIN_EMAIL) is not None:
            return
        admin_email = normalize_email(settings.ADMIN_EMAIL)
        db.add(User(
            email=admin_email,
            email_lookup=lookup_hash(admin_email),
            full_name=settings.ADMIN_FULL_NAME,
            role=Role.ADMINISTRATOR,
            is_active=True,
            hashed_password=password_hash.hash(settings.ADMIN_PASSWORD.get_secret_value()),
        ))
        await db.commit()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    try:
        await seed_admin()
    except Exception:
        pass
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
    app.mount("/static", StaticFiles(directory="static"), name="static")
    return app


app = create_app()
