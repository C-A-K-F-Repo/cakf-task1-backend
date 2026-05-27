from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from app.core.security import password_hash
from app.models.user import User
from app.schemas.user import UserCreate


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: UUID | str) -> User | None:
        """Get user by ID."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """Get user by email."""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create(self, user: UserCreate) -> User:
        """Create a new user."""
        user_data = user.model_dump()
        raw_password = user_data.pop("password")
        user_data["hashed_password"] = password_hash.hash(raw_password)
        
        new_user = User(**user_data)

        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def create_from_oauth(self, email: str) -> User:
        new_user = User(
            email=email,
        )

        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def delete(self, user_id: UUID) -> None:
        """Delete a user by ID."""
        await self.db.execute(delete(User).where(User.id == user_id))
        await self.db.commit()

    async def set_active(self, email: str, active: bool) -> None:
        """Set the user active status."""
        await self.db.execute(
            update(User)
            .where(User.email == email)
            .values(is_active=active)
        )
        await self.db.commit()

    async def update_password(self, email: str, new_password: str):
        """Update the user's password."""
        hashed_password = password_hash.hash(new_password)
        result = await self.db.execute(
            update(User)
            .where(User.email == email)
            .values(hashed_password=hashed_password)
        )
        await self.db.commit()

    async def update(self, user_id: UUID, **kwargs) -> User:
        """Update user fields."""
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(**kwargs)
        )
        await self.db.commit()
        return await self.get_by_id(user_id)

    async def get_by_phone(self, phone_number: str) -> User | None:
        """Get user by phone number."""
        result = await self.db.execute(select(User).where(User.phone_number == phone_number))
        return result.scalar_one_or_none()

    async def get_phone_numbers_by_ids(self, user_ids: list[UUID]) -> list[str]:
        """Get phone numbers for multiple user IDs."""
        result = await self.db.execute(
            select(User.phone_number).where(User.id.in_(user_ids), User.phone_number.is_not(None))
        )
        return [row[0] for row in result.all()]

    async def get_emails_by_ids(self, user_ids: list[UUID]) -> list[str]:
        """Get emails for multiple user IDs."""
        result = await self.db.execute(
            select(User.email).where(User.id.in_(user_ids), User.email.is_not(None))
        )
        return [row[0] for row in result.all()]

    async def get_all_phone_numbers(self) -> list[str]:
        """Get all phone numbers."""
        result = await self.db.execute(
            select(User.phone_number).where(User.phone_number.is_not(None))
        )
        return [row[0] for row in result.all()]

    async def get_all_emails(self) -> list[str]:
        """Get all emails."""
        result = await self.db.execute(
            select(User.email).where(User.email.is_not(None))
        )
        return [row[0] for row in result.all()]
