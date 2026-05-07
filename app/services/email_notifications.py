import ssl
import secrets
import logging
from email.message import EmailMessage

import aiosmtplib
import jwt
from aiosmtplib import SMTP
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.redis import get_redis_client
from app.repositories import UserRepository

from datetime import datetime, timedelta, UTC

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self.host = 'smtp.gmail.com'
        self.port = 465
        self.password = settings.APP_PASSWORD.get_secret_value()
        self.context = ssl.create_default_context()

    async def send_verification_email(self, email):
        token = jwt.encode({"email": email, "exp": datetime.now(UTC) + timedelta(minutes=10)}, settings.JWT_SECRET.get_secret_value(), algorithm="HS256")
        url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
        message = f"""
                    <html>
                    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; text-align: center;">
                        <div style="max-width: 400px; margin: auto; padding: 20px; border: 1px solid #eee; border-radius: 10px;">
                            <h2 style="color: #2c3e50;">Підтвердження пошти</h2>
                            <p>Посилання:</p>

                            <div style="background: #f8f9fa; padding: 15px; font-size: 28px; font-weight: bold; 
                                        letter-spacing: 8px; color: #007bff; border-radius: 5px; margin: 20px 0;">
                                {url}
                            </div>

                            <p style="font-size: 13px; color: #777;">
                                Код дійсний 5 хвилин.<br>
                                Якщо ви не запитували код, просто ігноруйте цей лист.
                            </p>
                        </div>
                    </body>
                    </html>
                    """

        await self.send_email(email, "Підтвердження пошти", message)

        return token

    async def send_email(self, email, subject, message):
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = settings.FROM_EMAIL
        msg['To'] = email
        msg.set_content(message)
        msg.add_alternative(message, subtype="html")

        smtp_client= SMTP(
            hostname=self.host,
            port=self.port,
            use_tls=True,
            tls_context=self.context
            )
        async with smtp_client:
            await smtp_client.login(settings.FROM_EMAIL, settings.APP_PASSWORD.get_secret_value())
            await smtp_client.send_message(msg)

    async def send_recovery_email(self, email):
        redis = await get_redis_client()

        recovery_code= secrets.token_hex(3).upper()

        message = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; text-align: center;">
                <div style="max-width: 400px; margin: auto; padding: 20px; border: 1px solid #eee; border-radius: 10px;">
                    <h2 style="color: #2c3e50;">Відновлення пароля</h2>
                    <p>Ваш код підтвердження:</p>
    
                    <div style="background: #f8f9fa; padding: 15px; font-size: 28px; font-weight: bold; 
                                letter-spacing: 8px; color: #007bff; border-radius: 5px; margin: 20px 0;">
                        {recovery_code}
                    </div>
    
                    <p style="font-size: 13px; color: #777;">
                        Код дійсний 5 хвилин.<br>
                        Якщо ви не запитували код, просто ігноруйте цей лист.
                    </p>
                </div>
            </body>
            </html>
            """
        try:
            await self.send_email(email, 'Код для відновлення пароля.', message)
            await redis.setex(name=email, time=300, value=recovery_code)
        except aiosmtplib.errors.SMTPException as e:
            logger.error(f"Error sending email: {e}")
            return None

    @staticmethod
    async def verify(email: str,user_code: str) -> bool:
        redis = await get_redis_client()

        r_code = await redis.get(email)
        if not r_code:
            return False
        if r_code == user_code.upper():
            await redis.delete(email)
            return True
        return False

    @staticmethod
    async def verify_token(db: AsyncSession, token: str) -> str | None:
        try:
            payload = jwt.decode(token, settings.JWT_SECRET.get_secret_value(), algorithms=["HS256"])
            await UserRepository(db).set_active(payload["email"], True)
            return payload["email"]
        except jwt.ExpiredSignatureError:
            return None


email_service = EmailService()
