import uuid
from datetime import date

from typing import TYPE_CHECKING
from sqlalchemy import UUID, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.personal_data_crypto import EncryptedDate, EncryptedString
from app.models.base import Base
from app.models.roles import Role

if TYPE_CHECKING:
    from app.models.order import OrderModel


class User(Base):
    __tablename__ = 'users'

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)

    email: Mapped[str] = mapped_column(EncryptedString, nullable=False)
    email_lookup: Mapped[str] = mapped_column(String(64), index=True, unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(EncryptedString, nullable=True)
    phone_number: Mapped[str] = mapped_column(EncryptedString, nullable=True)
    phone_number_lookup: Mapped[str] = mapped_column(String(64), index=True, unique=True, nullable=True)
    role: Mapped[Role] = mapped_column(default=Role.USER)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    dob: Mapped[date] = mapped_column(EncryptedDate, nullable=True)
    delivery_address: Mapped[str] = mapped_column(EncryptedString, nullable=True)

    orders: Mapped[list["OrderModel"]] = relationship(back_populates="user")

    @property
    def has_password(self) -> bool:
        return self.hashed_password is not None
