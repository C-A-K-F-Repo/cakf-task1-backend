import asyncio
import ssl
import secrets
from email.message import EmailMessage
from aiosmtplib import SMTP
from app.core.config import settings
from app.core.redis import get_redis_client

class EmailService:
    def __init__(self):
        self.host = 'smtp.gmail.com'
        self.port = 465
        self.from_email = settings.FROM_EMAIL
        self.password = settings.APP_PASSWORD.get_secret_value()
        self.context = ssl.create_default_context()

    async def send_recovery_email(self,email):
        redis = await get_redis_client()

        recovery_code= secrets.token_hex(3).upper()
        msg = EmailMessage()
        msg['Subject'] = 'Код для відновлення пароля.'
        msg['From'] = self.from_email
        msg['To'] = email
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
        msg.add_alternative(message, subtype="html")

        try:
            smtp_client= SMTP(
                hostname=self.host,
                port=self.port,
                use_tls=True,
                tls_context=self.context
                )
            async with smtp_client:
                await smtp_client.login(self.from_email, self.password)
                await smtp_client.send_message(msg)
            await redis.setex(name=email, time=300, value=recovery_code)
            return recovery_code
        except Exception as e:
            print(f"Error:{e}")
            return None

    async def verify(self,email:str,user_code:str) -> bool:
        redis = await get_redis_client()

        r_code = await redis.get(email)
        if not r_code:
            return False
        if r_code == user_code.upper():
            await redis.delete(email)
            return True
        return False




email_service = EmailService()

