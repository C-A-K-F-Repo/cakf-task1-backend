from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.models import OrderModel, OrderItem
from app.schemas.order import OrderIn


class OrderRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: UUID, order_in: OrderIn):
        new_order = OrderModel(
            user_id=user_id,
        )
        self.db.add(new_order)
        await self.db.flush()

        for item in order_in.items:
            order_item = OrderItem(
                order_id=new_order.id,
                product_id=item.product_id,
                quantity=item.quantity
            )
            self.db.add(order_item)

        await self.db.commit()
        await self.db.refresh(new_order)

        # Re-fetch with items and products for the response
        stmt = (
            select(OrderModel)
            .where(OrderModel.id == new_order.id)
            .options(selectinload(OrderModel.items).joinedload(OrderItem.product))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def get(self, limit: int = 100, skip: int = 0):
        stmt = (
            select(OrderModel)
            .offset(skip)
            .limit(limit)
            .options(selectinload(OrderModel.items).joinedload(OrderItem.product))
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_all_with_users(self, limit: int = 100, skip: int = 0):
        stmt = (
            select(OrderModel)
            .order_by(OrderModel.date.desc())
            .offset(skip)
            .limit(limit)
            .options(
                selectinload(OrderModel.items).joinedload(OrderItem.product),
                joinedload(OrderModel.user),
            )
        )
        result = await self.db.execute(stmt)
        return result.unique().scalars().all()

    async def delete_by_id(self, order_id: UUID):
        await self.db.execute(delete(OrderItem).where(OrderItem.order_id == order_id))
        await self.db.execute(delete(OrderModel).where(OrderModel.id == order_id))
        await self.db.commit()

    async def get_by_user(self, user_id: UUID):
        stmt = (
            select(OrderModel)
            .where(OrderModel.user_id == user_id)
            .options(selectinload(OrderModel.items).joinedload(OrderItem.product))
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_by_id(self, order_id: UUID):
        stmt = (
            select(OrderModel)
            .where(OrderModel.id == order_id)
            .options(selectinload(OrderModel.items).joinedload(OrderItem.product))
        )
        result = await self.db.execute(stmt)
        order = result.scalar_one_or_none()
        return order


    async def delete_selected_for_user(self, user_id: UUID, order_ids: list[UUID]):
        # Delete order items first to avoid foreign key violation
        # We only delete items for orders that belong to the user
        item_stmt = delete(OrderItem).where(
            OrderItem.order_id.in_(
                select(OrderModel.id).where(
                    OrderModel.user_id == user_id, 
                    OrderModel.id.in_(order_ids)
                )
            )
        )
        await self.db.execute(item_stmt)

        stmt = delete(OrderModel).where(OrderModel.user_id == user_id, OrderModel.id.in_(order_ids))
        await self.db.execute(stmt)
        await self.db.commit()

    async def delete_all_for_user(self, user_id: UUID):
        # Delete all order items for this user's orders
        item_stmt = delete(OrderItem).where(
            OrderItem.order_id.in_(
                select(OrderModel.id).where(OrderModel.user_id == user_id)
            )
        )
        await self.db.execute(item_stmt)

        await self.db.execute(delete(OrderModel).where(OrderModel.user_id == user_id))
        await self.db.commit()

    async def delete_by_user(self, user_id: UUID):
        # Delete order items first to avoid foreign key violation
        item_stmt = delete(OrderItem).where(
            OrderItem.order_id.in_(
                select(OrderModel.id).where(OrderModel.user_id == user_id)
            )
        )
        await self.db.execute(item_stmt)

        stmt = delete(OrderModel).where(OrderModel.user_id == user_id)
        await self.db.execute(stmt)
        await self.db.commit()
