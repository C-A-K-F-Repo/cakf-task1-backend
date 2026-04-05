from contextlib import asynccontextmanager

from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from twilio.http.async_http_client import AsyncTwilioHttpClient

from app.core.config import settings
from app.exceptions.sms import OtpSendError, OtpVerifyError, SmsSendError


class SmsService:
    @asynccontextmanager
    async def _client(self):
        http_client = AsyncTwilioHttpClient()
        try:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN.get_secret_value(), http_client=http_client)
            yield client
        finally:
            await http_client.session.close()

    async def send_otp(self, phone_num: str) -> None:
        try:
            async with self._client() as client:
                return await client.verify.v2.services(settings.TWILIO_SERVICE_SID).verifications.create_async(
                    to=phone_num,
                    channel='sms',
                )
        except TwilioRestException as e:
            raise OtpSendError(f"Failed to send OTP") from e
        except Exception as e:
            raise OtpSendError("Unexpected error while sending OTP") from e

    async def verify_otp(self, phone_num: str, code: str) -> bool:
        try:
            async with self._client() as client:
                resp = await client.verify.v2.services(settings.TWILIO_SERVICE_SID).verification_checks.create_async(
                    to=phone_num,
                    code=code
                )
                return resp.status == "approved"
        except TwilioRestException as e:
            raise OtpVerifyError(f"Failed to verify OTP") from e
        except Exception as e:
            raise OtpVerifyError("Unexpected error while verifying OTP") from e
    
    async def send_msg(self, phone_num: str, content: str) -> None:
        try:
            async with self._client() as client:
                await client.messages.create_async(
                    to=phone_num,
                    body=content,
                    from_=settings.TWILIO_SENDER_PHONE
                )
        except TwilioRestException as e:
            raise SmsSendError("Failed to send sms") from e
        except Exception as e:
            raise SmsSendError("Unexpected error while sending SMS") from e
