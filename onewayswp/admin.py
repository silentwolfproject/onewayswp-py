import json
from pathlib import Path
from typing import Optional, Tuple

from ._core import get_core, detect_platform
from .exceptions import (
    OnewaySWPError,
    SecurityError,
    InvalidKeyError,
    raise_from_response,
)


SECRET_FILE = "secret.key"
PUBLIC_FILE = "public.key"
DEFAULT_DIR = Path.home() / ".owswp"


class Admin:
    def __init__(self, key_dir: Optional[str] = None) -> None:
        self.key_dir: Path = Path(key_dir).expanduser() if key_dir else DEFAULT_DIR
        self.secret_key: Optional[str] = None
        self.public_key: Optional[str] = None
        self._core = get_core()

    def keys_exist(self, key_dir: Optional[str] = None) -> bool:
        check_dir = Path(key_dir).expanduser() if key_dir else self.key_dir
        secret_path = check_dir / SECRET_FILE
        public_path = check_dir / PUBLIC_FILE
        return secret_path.exists() and public_path.exists()

    def generate_keys(
        self,
        auto_save: bool = True,
        file_path: Optional[str] = None,
    ) -> Tuple[str, str]:
        response = self._core.generate_key_pair()
        if not response.get("status"):
            raise_from_response(response)

        self.secret_key = response.get("secret_key")
        self.public_key = response.get("public_key")

        if auto_save:
            save_dir = Path(file_path).expanduser() if file_path else self.key_dir
            self.save_keys(target_dir=str(save_dir))

        return self.secret_key, self.public_key

    def save_keys(self, target_dir: Optional[str] = None) -> None:
        if not self.secret_key or not self.public_key:
            raise OnewaySWPError("No keys to save. Call generate_keys() first.")

        save_dir = Path(target_dir).expanduser() if target_dir else self.key_dir
        save_dir.mkdir(parents=True, exist_ok=True)

        secret_path = save_dir / SECRET_FILE
        public_path = save_dir / PUBLIC_FILE

        secret_path.write_text(self.secret_key)
        public_path.write_text(self.public_key)

        try:
            secret_path.chmod(0o600)
        except (OSError, NotImplementedError):
            pass

    def load_keys(
        self,
        key_dir: Optional[str] = None,
        validate: bool = True,
        auto_generate: bool = False,
    ) -> Tuple[str, str]:
        load_dir = Path(key_dir).expanduser() if key_dir else self.key_dir
        secret_path = load_dir / SECRET_FILE
        public_path = load_dir / PUBLIC_FILE

        if not secret_path.exists() or not public_path.exists():
            if auto_generate:
                self.key_dir = load_dir
                self.generate_keys(auto_save=True, file_path=str(load_dir))
                if validate:
                    self.validate_keys()
                return self.secret_key, self.public_key
            raise InvalidKeyError(f"Key files not found in {load_dir}")

        self.secret_key = secret_path.read_text().strip()
        self.public_key = public_path.read_text().strip()

        if validate:
            self.validate_keys()

        return self.secret_key, self.public_key

    def set_keys(
        self,
        secret_key: str,
        public_key: str,
        validate: bool = True,
    ) -> None:
        if not secret_key or not public_key:
            raise InvalidKeyError("Both secret_key and public_key required")

        self.secret_key = secret_key.strip()
        self.public_key = public_key.strip()

        if validate:
            self.validate_keys()

    def validate_keys(self) -> bool:
        if not self.secret_key or not self.public_key:
            raise InvalidKeyError("Keys not loaded")

        response = self._core.validate_key_pair(self.secret_key, self.public_key)
        if not response.get("status"):
            raise SecurityError(
                response.get("message", "Key mismatch"),
                code=response.get("code"),
            )
        return True

    def create_license(
        self,
        type: str = "date",
        expires: Optional[str] = None,
        credits: Optional[int] = None,
        duration_seconds: Optional[int] = None,
        hours: Optional[float] = None,
        additional_data: Optional[dict] = None,
    ) -> dict:
        if not self.secret_key:
            raise OnewaySWPError(
                "Secret key not loaded. Call load_keys() or generate_keys()."
            )

        if type not in ("date", "credit", "duration"):
            raise OnewaySWPError(
                f"Invalid type '{type}'. Must be: date, credit, duration"
            )

        if type == "date" and not expires:
            raise OnewaySWPError("type='date' requires 'expires' (YYYY-MM-DD)")

        if type == "credit" and credits is None:
            raise OnewaySWPError("type='credit' requires 'credits'")

        if type == "duration" and duration_seconds is None and hours is None:
            raise OnewaySWPError(
                "type='duration' requires 'duration_seconds' or 'hours'"
            )

        payload: dict = {}
        if expires:
            payload["expires"] = expires
        if credits is not None:
            payload["credits"] = credits
        if duration_seconds is not None:
            payload["duration_seconds"] = duration_seconds
        elif hours is not None:
            payload["duration_seconds"] = int(hours * 3600)
        if additional_data:
            payload["additional_data"] = additional_data

        response = self._core.create_license(
            self.secret_key,
            type,
            json.dumps(payload),
        )

        if not response.get("status"):
            raise_from_response(response)

        return response

    def regenerate_keys(self, key_dir: Optional[str] = None) -> Tuple[str, str]:
        target_dir = Path(key_dir).expanduser() if key_dir else self.key_dir
        return self.generate_keys(auto_save=True, file_path=str(target_dir))

    def platform(self) -> dict:
        os_name, arch = detect_platform()
        return {"os": os_name, "arch": arch}

    def version(self) -> str:
        response = self._core.version()
        if not response.get("status"):
            raise_from_response(response)
        return response.get("version", "")