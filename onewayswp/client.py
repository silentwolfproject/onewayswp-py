from pathlib import Path
from typing import Optional, List

from ._core import get_core, retry_on_locked
from .exceptions import (
    OnewaySWPError,
    SecurityError,
    InvalidKeyError,
    InvalidTokenError,
    raise_from_response,
)


class Client:
    def __init__(
        self,
        data_path: Optional[str] = None,
        extra_paths: Optional[List[str]] = None,
    ) -> None:
        self.data_path: Path = (
            Path(data_path).expanduser()
            if data_path
            else Path.cwd() / "license.swpb"
        )
        self.extra_paths: List[Path] = (
            [Path(p).expanduser() for p in extra_paths] if extra_paths else []
        )
        self.public_key: Optional[str] = None
        self._last_status: Optional[dict] = None
        self._core = get_core()

    def open_key(self, path: str) -> None:
        p = Path(path).expanduser()

        if p.is_dir():
            p = p / "public.key"

        if not p.exists():
            raise InvalidKeyError(f"Key file not found: {p}")

        content = p.read_text().strip()
        self.set_public_key(content)

    def set_public_key(self, key: str) -> None:
        if not key:
            raise InvalidKeyError("Public key is empty")

        key = key.strip()

        if key.startswith("OWSWP-sec-"):
            raise SecurityError(
                "Security error: you provided a secret key. "
                "Client must use public key only."
            )

        if not key.startswith("OWSWP-pub-"):
            raise InvalidKeyError(
                "Invalid key format. Must start with 'OWSWP-pub-'"
            )

        self.public_key = key

    def is_active(self) -> bool:
        if not self.public_key:
            return False

        if not self.data_path.exists():
            return False

        try:
            result = self.protection_verify()
            return result.get("status", False)
        except Exception:
            return False

    def validate_key(self, token: str) -> dict:
        if not self.public_key:
            raise InvalidKeyError(
                "Public key not set. Call open_key() or set_public_key()."
            )

        if not token or not isinstance(token, str):
            raise OnewaySWPError("Token is required and must be a string")

        token = token.strip()

        if not token.startswith("OWSWP-"):
            raise InvalidTokenError(
                "Invalid token format. Must start with 'OWSWP-'"
            )

        try:
            self.data_path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise OnewaySWPError(f"Cannot create directory: {e}")

        response = retry_on_locked(
            self._core.validate_key,
            token,
            self.public_key,
            str(self.data_path),
        )
        self._last_status = response
        return response

    def inspect_key(self, token: str) -> dict:
        if not self.public_key:
            raise InvalidKeyError("Public key not set.")

        if not token or not isinstance(token, str):
            raise OnewaySWPError("Token is required and must be a string")

        response = self._core.inspect_key(token.strip(), self.public_key)
        return response

    def protection_verify(self) -> dict:
        if not self.public_key:
            raise InvalidKeyError("Public key not set.")

        if not self.data_path.exists():
            return {
                "status": False,
                "code": "NO_STATE_FILE",
                "message": f"State file not found: {self.data_path}",
            }

        response = retry_on_locked(
            self._core.protection_verify,
            self.public_key,
            str(self.data_path),
        )
        self._last_status = response
        return response

    def use_credit(self, amount: int = 1) -> dict:
        if not self.public_key:
            raise InvalidKeyError("Public key not set.")

        if not self.data_path.exists():
            raise OnewaySWPError("State file not found. Validate key first.")

        if amount <= 0:
            raise OnewaySWPError("Amount must be greater than zero")

        response = retry_on_locked(
            self._core.decrement_credit,
            self.public_key,
            str(self.data_path),
            amount,
        )
        self._last_status = response
        return response

    def session(self):
        return _SessionContext(self)

    def _start_session(self) -> dict:
        if not self.public_key:
            raise InvalidKeyError("Public key not set.")
        if not self.data_path.exists():
            raise OnewaySWPError("State file not found. Validate key first.")
        return self._core.start_session(self.public_key, str(self.data_path))

    def _stop_session(self) -> dict:
        if not self.public_key:
            raise InvalidKeyError("Public key not set.")
        if not self.data_path.exists():
            raise OnewaySWPError("State file not found. Validate key first.")
        return self._core.stop_session(self.public_key, str(self.data_path))

    def export_state(self) -> dict:
        if not self.public_key:
            raise InvalidKeyError("Public key not set.")
        if not self.data_path.exists():
            raise OnewaySWPError("State file not found.")
        return self._core.export_state(self.public_key, str(self.data_path))

    def import_state(self, data) -> dict:
        if not self.public_key:
            raise InvalidKeyError("Public key not set.")

        try:
            self.data_path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise OnewaySWPError(f"Cannot create directory: {e}")

        if isinstance(data, dict):
            import json as _json
            data = _json.dumps(data)

        response = self._core.import_state(
            self.public_key,
            str(self.data_path),
            data,
        )
        self._last_status = response
        return response

    def status(self) -> dict:
        if self._last_status:
            return self._last_status

        if not self.data_path.exists():
            return {
                "status": False,
                "code": "NO_STATE_FILE",
                "message": "No status available",
            }

        return self.protection_verify()

    def state_path(self) -> str:
        return str(self.data_path)

    def reset(self) -> None:
        if self.data_path.exists():
            self.data_path.unlink()
        self._last_status = None

    def version(self) -> str:
        response = self._core.version()
        if not response.get("status"):
            raise_from_response(response)
        return response.get("version", "")


class _SessionContext:
    def __init__(self, client: Client) -> None:
        self.client = client
        self._started = False

    def __enter__(self) -> Client:
        result = self.client._start_session()
        if not result.get("status"):
            raise_from_response(result)
        self._started = True
        return self.client

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if self._started:
            try:
                self.client._stop_session()
            except Exception:
                pass
        return False