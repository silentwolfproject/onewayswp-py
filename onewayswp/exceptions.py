class OnewaySWPError(Exception):
    def __init__(self, message: str, code: str = None):
        super().__init__(message)
        self.code = code

    def __str__(self) -> str:
        if self.code:
            return f"[{self.code}] {self.args[0]}"
        return self.args[0]


class InvalidTokenError(OnewaySWPError):
    pass


class ExpiredError(OnewaySWPError):
    pass


class ClockRollbackError(OnewaySWPError):
    pass


class SecurityError(OnewaySWPError):
    pass


class InvalidKeyError(OnewaySWPError):
    pass


class CorruptedFileError(OnewaySWPError):
    pass


class InsufficientCreditError(OnewaySWPError):
    pass


class FileLockedError(OnewaySWPError):
    pass


class PlatformNotSupportedError(OnewaySWPError):
    pass


class CoreLoadError(OnewaySWPError):
    pass


class NoActiveSessionError(OnewaySWPError):
    pass


CODE_TO_EXCEPTION = {
    "INVALID_SIGNATURE": InvalidTokenError,
    "INVALID_MAGIC": CorruptedFileError,
    "INVALID_KEY_FORMAT": InvalidKeyError,
    "UNSUPPORTED_VERSION": CorruptedFileError,
    "KEY_MISMATCH": SecurityError,
    "SECURITY_ERROR": SecurityError,
    "EXPIRED": ExpiredError,
    "CLOCK_ROLLBACK_DETECTED": ClockRollbackError,
    "CORRUPTED_FILE": CorruptedFileError,
    "INSUFFICIENT_CREDITS": InsufficientCreditError,
    "FILE_LOCKED": FileLockedError,
    "IO_ERROR": OnewaySWPError,
    "CRYPTO_ERROR": OnewaySWPError,
    "SERIALIZATION_ERROR": OnewaySWPError,
    "FFI_ERROR": OnewaySWPError,
    "NULL_POINTER": CoreLoadError,
}


def raise_from_response(response: dict) -> None:
    code = response.get("code", "UNKNOWN")
    message = response.get("message", "Unknown error")
    exc_class = CODE_TO_EXCEPTION.get(code, OnewaySWPError)
    raise exc_class(message, code=code)