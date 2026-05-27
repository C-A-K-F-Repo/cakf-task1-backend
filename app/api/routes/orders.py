from fastapi import APIRouter, status, HTTPException, Depends, Request

from app.core.audit import audit_event
from app.dependencies.db import SessionDep
from app.dependencies.user import get_current_user, get_current_active_user, allow_staff, allow_admin
from app.repositories.order import OrderRepository
from app.schemas.order import OrderIn, OrderOut, OrderAdminOut
import uuid

router = APIRouter()


@router.post("/", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
async def create_order(order_in: OrderIn, db: SessionDep, request: Request, current_user = Depends(get_current_user)):
    order = await OrderRepository(db).create(current_user["sub"], order_in)
    audit_event(
        "order.create",
        "success",
        actor_user_id=current_user.get("sub"),
        actor_role=current_user.get("role"),
        target_type="order",
        target_id=order.id,
        metadata={"item_count": len(order_in.items)},
        request=request,
    )
    return order


@router.get("/", response_model=list[OrderAdminOut], dependencies=[Depends(allow_staff)])
async def get_all_orders(db: SessionDep, request: Request, limit: int = 100, skip: int = 0, current_user = Depends(get_current_user)):
    orders = await OrderRepository(db).get_all_with_users(limit=limit, skip=skip)
    audit_event("order.list.staff", "success", actor_user_id=current_user.get("sub"), actor_role=current_user.get("role"), metadata={"limit": limit, "skip": skip, "result_count": len(orders)}, request=request)
    return [
        OrderAdminOut(
            id=order.id,
            user_id=order.user_id,
            user_email=order.user.email if order.user else None,
            user_full_name=order.user.full_name if order.user else None,
            items=order.items,
            date=order.date,
        )
        for order in orders
    ]


@router.delete("/admin/{order_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(allow_admin)])
async def admin_delete_order(order_id: uuid.UUID, db: SessionDep, request: Request, current_user = Depends(get_current_user)):
    await OrderRepository(db).delete_by_id(order_id)
    audit_event("order.delete.admin", "success", actor_user_id=current_user.get("sub"), actor_role=current_user.get("role"), target_type="order", target_id=order_id, request=request)
    return None


@router.get("/me", response_model=list[OrderOut])
async def get_orders_for_user(db: SessionDep, request: Request, current_user = Depends(get_current_user)):
    orders = await OrderRepository(db).get_by_user(current_user["sub"])
    audit_event("order.list.self", "success", actor_user_id=current_user.get("sub"), actor_role=current_user.get("role"), metadata={"result_count": len(orders)}, request=request)
    return orders


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_orders(order_ids: list[uuid.UUID] | None, db: SessionDep, request: Request, current_user = Depends(get_current_user)):
    if not order_ids:
        await OrderRepository(db).delete_all_for_user(current_user["sub"])
        audit_event("order.delete.self_all", "success", actor_user_id=current_user.get("sub"), actor_role=current_user.get("role"), request=request)
    else:
        await OrderRepository(db).delete_selected_for_user(current_user["sub"], order_ids)
        audit_event("order.delete.self_selected", "success", actor_user_id=current_user.get("sub"), actor_role=current_user.get("role"), metadata={"selected_count": len(order_ids)}, request=request)


@router.get("/{order_id}", response_model=OrderOut)
async def get_order(order_id: uuid.UUID, db: SessionDep, request: Request, current_user = Depends(get_current_active_user)):
    order = await OrderRepository(db).get_by_id(order_id)
    if not order:
        audit_event("order.read", "failure", actor_user_id=current_user.id, actor_role=current_user.role.value, target_type="order", target_id=order_id, metadata={"reason": "not_found"}, request=request)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if str(order.user_id) != str(current_user.id) and current_user.role.value not in {"Administrator", "Advanced_User"}:
        audit_event("order.read", "denied", actor_user_id=current_user.id, actor_role=current_user.role.value, target_type="order", target_id=order_id, request=request)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    audit_event("order.read", "success", actor_user_id=current_user.id, actor_role=current_user.role.value, target_type="order", target_id=order_id, request=request)
    return order
