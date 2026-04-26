from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.models.user import User
from app.schemas.user import UserCreate


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: UUID) -> User | None:
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
        # TODO: Hash the password before storing it
        user_data["hashed_password"] = raw_password
        
        new_user = User(**user_data)

        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def delete(self, user_id: UUID) -> None:
        """Delete a user by ID."""
        await self.db.execute(delete(User).where(User.id == user_id))
        await self.db.commit()

    async def set_active(self, user_id: UUID, active: bool) -> None:
        """Set the user active status."""
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(is_active=active)
        )
        await self.db.commit()
