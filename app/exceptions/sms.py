class SmsServiceError(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class SmsSendError(SmsServiceError):
    def __init__(self, message):
        super().__init__(message, status_code=400)


class OtpSendError(SmsServiceError):
    def __init__(self, message):
        super().__init__(message, status_code=400)


class OtpVerifyError(SmsServiceError):
    def __init__(self, message):
        super().__init__(message, status_code=400)
