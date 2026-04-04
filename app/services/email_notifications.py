import smtplib
import ssl
import secrets
from email.message import EmailMessage
import os
from dotenv import load_dotenv

load_dotenv()

class EmailService:
    def __init__(self):
        self.host = 'smtp.gmail.com'
        self.port = 465
        self.from_email = os.getenv('FROM_EMAIL')
        self.password = os.getenv('PASSWORD')
        self.context = ssl.create_default_context()

    def send_recovery_email(self,email):
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
                        Код дійсний 15 хвилин.<br>
                        Якщо ви не запитували код, просто ігноруйте цей лист.
                    </p>
                </div>
            </body>
            </html>
            """
        msg.add_alternative(message, subtype="html")

        try:
            with smtplib.SMTP_SSL(self.host, self.port,context=self.context) as smtp:
                smtp.login(self.from_email, self.password)
                smtp.send_message(msg)
        except Exception as e:
            print(f"Error:{e}")

email_service = EmailService()

