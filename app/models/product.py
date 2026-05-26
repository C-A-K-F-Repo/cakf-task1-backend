import uuid

from sqlalchemy import UUID, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from .base import Base

if TYPE_CHECKING:
    from .order import OrderItem


class Product(Base):
    __tablename__ = 'products'

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), index=True)
    price: Mapped[float] = mapped_column(nullable=False)
    product_type_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("product_types.id"), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    image_url: Mapped[str] = mapped_column(String(500), nullable=True)

    __table_args__ = (
        UniqueConstraint('name', 'product_type_id'),
    )

    order_items: Mapped[list["OrderItem"]] = relationship(back_populates="product", cascade="all, delete-orphan")
