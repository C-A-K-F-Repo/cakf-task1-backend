import uuid
from datetime import date

from typing import TYPE_CHECKING
from sqlalchemy import UUID, String, Boolean, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.schemas.user import Role

if TYPE_CHECKING:
    from app.models.order import OrderModel


class User(Base):
    __tablename__ = 'users'

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)

    email: Mapped[str] = mapped_column(String(100), index=True, unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), index=True, nullable=True)
    phone_number: Mapped[str] = mapped_column(String(20), index=True, nullable=True, unique=True)
    role: Mapped[Role] = mapped_column(default=Role.USER)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    dob: Mapped[date] = mapped_column(Date, nullable=True)
    delivery_address: Mapped[str] = mapped_column(String(255), nullable=True)

    orders: Mapped[list["OrderModel"]] = relationship(back_populates="user")
