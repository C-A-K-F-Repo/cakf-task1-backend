"""Notifications routes."""

from fastapi import APIRouter

router = APIRouter()


@router.post("/promotions")
async def send_promotions():
    return "Promotions sent"


@router.post("/birthday")
async def send_birthday_discount():
    return "Birthday discount sent"
