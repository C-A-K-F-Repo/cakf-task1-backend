import logging
from contextlib import asynccontextmanager

from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from twilio.http.async_http_client import AsyncTwilioHttpClient
from opentelemetry import trace

from app.core.config import settings
from app.exceptions.sms import OtpSendError, OtpVerifyError, SmsSendError


logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


class SmsService:
    @staticmethod
    @asynccontextmanager
    async def _client():
        http_client = AsyncTwilioHttpClient()
        try:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN.get_secret_value(),
                            http_client=http_client)
            yield client
        finally:
            await http_client.session.close()
    
    async def send_otp(self, phone_num: str) -> None:
        phone_suffix = _phone_suffix(phone_num)

        with tracer.start_as_current_span("sms.send_otp") as span:
            span.set_attribute("sms.channel", "sms")
            span.set_attribute("sms.phone_suffix", phone_suffix)
            logger.info("Sending OTP to phone ending in %s", phone_suffix)

            try:
                async with self._client() as client:
                    await client.verify.v2.services(settings.TWILIO_SERVICE_SID).verifications.create_async(
                        to=phone_num,
                        channel='sms',
                    )
            except TwilioRestException as e:
                span.record_exception(e)
                logger.exception("Twilio failed while sending OTP to phone ending in %s", phone_suffix)
                raise OtpSendError("Failed to send OTP") from e
            except Exception as e:
                span.record_exception(e)
                logger.exception("Unexpected error while sending OTP to phone ending in %s", phone_suffix)
                raise OtpSendError("Unexpected error while sending OTP") from e

    async def verify_otp(self, phone_num: str, code: str) -> bool:
        phone_suffix = _phone_suffix(phone_num)

        with tracer.start_as_current_span("sms.verify_otp") as span:
            span.set_attribute("sms.phone_suffix", phone_suffix)
            logger.info("Verifying OTP for phone ending in %s", phone_suffix)

            try:
                async with self._client() as client:
                    resp = await client.verify.v2.services(settings.TWILIO_SERVICE_SID).verification_checks.create_async(
                        to=phone_num,
                        code=code
                    )
                    approved = resp.status == "approved"
                    span.set_attribute("sms.otp_approved", approved)
                    logger.info("OTP verification completed for phone ending in %s approved=%s", phone_suffix, approved)
                    return approved
            except TwilioRestException as e:
                span.record_exception(e)
                logger.exception("Twilio failed while verifying OTP for phone ending in %s", phone_suffix)
                raise OtpVerifyError("Failed to verify OTP") from e
            except Exception as e:
                span.record_exception(e)
                logger.exception("Unexpected error while verifying OTP for phone ending in %s", phone_suffix)
                raise OtpVerifyError("Unexpected error while verifying OTP") from e

    async def send_msg(self, phone_num: str, content: str) -> None:
        phone_suffix = _phone_suffix(phone_num)

        with tracer.start_as_current_span("sms.send_message") as span:
            span.set_attribute("sms.phone_suffix", phone_suffix)
            span.set_attribute("sms.message_length", len(content))
            logger.info("Sending SMS to phone ending in %s", phone_suffix)

            try:
                async with self._client() as client:
                    await client.messages.create_async(
                        to=phone_num,
                        body=content,
                        from_=settings.TWILIO_SENDER_PHONE
                    )
            except TwilioRestException as e:
                span.record_exception(e)
                logger.exception("Twilio failed while sending SMS to phone ending in %s", phone_suffix)
                raise SmsSendError("Failed to send sms") from e
            except Exception as e:
                span.record_exception(e)
                logger.exception("Unexpected error while sending SMS to phone ending in %s", phone_suffix)
                raise SmsSendError("Unexpected error while sending SMS") from e


def _phone_suffix(phone_num: str) -> str:
    return phone_num[-4:] if len(phone_num) >= 4 else phone_num
