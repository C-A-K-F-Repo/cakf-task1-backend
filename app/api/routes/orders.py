"""Orders routes."""

from fastapi import APIRouter

router = APIRouter()


@router.post("/")
async def create_order():
    return "Order created"


@router.get("/{id}")
async def get_order(id: str):
    return f"Order {id}"


@router.delete("/{id}")
async def delete_order(id: str):
    return f"Order {id} deleted"
