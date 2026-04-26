"""Health check routes."""

import logging

from fastapi import APIRouter

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/")
def health() -> dict[str, str]:
    logger.debug("Health check succeeded")
    return {"status": "ok"}
