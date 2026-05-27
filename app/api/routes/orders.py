from fastapi import APIRouter, status, HTTPException, Depends

from app.dependencies.db import SessionDep
from app.dependencies.user import get_current_user
from app.repositories.order import OrderRepository
from app.schemas.order import OrderIn, OrderOut
import uuid

router = APIRouter()


@router.post("/", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
async def create_order(order_in: OrderIn, db: SessionDep, current_user = Depends(get_current_user)):
    return await OrderRepository(db).create(current_user["sub"], order_in)


@router.get("/me", response_model=list[OrderOut])
async def get_orders_for_user(db: SessionDep, current_user = Depends(get_current_user)):
    return await OrderRepository(db).get_by_user(current_user["sub"])


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_orders(order_ids: list[uuid.UUID] | None, db: SessionDep, current_user = Depends(get_current_user)):
    if not order_ids:
        await OrderRepository(db).delete_all_for_user(current_user["sub"])
    else:
        await OrderRepository(db).delete_selected_for_user(current_user["sub"], order_ids)


@router.get("/{order_id}", response_model=OrderOut)
async def get_order(order_id: uuid.UUID, db: SessionDep):
    order = await OrderRepository(db).get_by_id(order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order
