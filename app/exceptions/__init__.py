from .sms import SmsServiceError

from fastapi import FastAPI
from fastapi.responses import JSONResponse


def register_exceptions(app: FastAPI):
    @app.exception_handler(SmsServiceError)
    async def sms_service_exception_handler(request, exc: SmsServiceError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message}
        )
