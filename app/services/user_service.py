import secrets
import logging
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis import get_redis_client
from app.models.user import User
from app.repositories.user import UserRepository
from app.services.email_notifications import email_service
from app.services.sms import SmsService

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.sms_service = SmsService()

    async def request_email_update(self, user: User, new_email: str):
        if await self.user_repo.get_by_email(new_email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use")

        redis = await get_redis_client()
        code = secrets.token_hex(3).upper()
        
        # Store pending email and code in redis
        await redis.setex(f"email_update:{user.id}", 600, f"{new_email}:{code}")
        
        message = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; text-align: center;">
                <div style="max-width: 400px; margin: auto; padding: 20px; border: 1px solid #eee; border-radius: 10px;">
                    <h2 style="color: #2c3e50;">Зміна пошти</h2>
                    <p>Ваш код підтвердження для нової пошти:</p>
    
                    <div style="background: #f8f9fa; padding: 15px; font-size: 28px; font-weight: bold; 
                                letter-spacing: 8px; color: #007bff; border-radius: 5px; margin: 20px 0;">
                        {code}
                    </div>
    
                    <p style="font-size: 13px; color: #777;">
                        Код дійсний 10 хвилин.
                    </p>
                </div>
            </body>
            </html>
            """
        await email_service.send_email(new_email, "Підтвердження зміни пошти", message)

    async def verify_email_update(self, user: User, code: str):
        redis = await get_redis_client()
        stored_data = await redis.get(f"email_update:{user.id}")
        
        if not stored_data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No pending email update found")
        
        new_email, stored_code = stored_data.split(":")
        
        if code.upper() != stored_code:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification code")
        
        await self.user_repo.update(user.id, email=new_email)
        await redis.delete(f"email_update:{user.id}")

    async def request_phone_update(self, user: User, new_phone: str):
        if await self.user_repo.get_by_phone(new_phone):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone number already in use")

        redis = await get_redis_client()
        # Twilio Verify handles code generation and storage, but we should remember which phone was requested
        await redis.setex(f"phone_update:{user.id}", 600, new_phone)
        
        await self.sms_service.send_otp(new_phone)

    async def verify_phone_update(self, user: User, code: str):
        redis = await get_redis_client()
        new_phone = await redis.get(f"phone_update:{user.id}")
        
        if not new_phone:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No pending phone update found")
        
        is_valid = await self.sms_service.verify_otp(new_phone, code)
        if not is_valid:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP")
        
        await self.user_repo.update(user.id, phone_number=new_phone)
        await redis.delete(f"phone_update:{user.id}")
