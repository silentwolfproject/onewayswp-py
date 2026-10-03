import ctypes
import json
import platform
import time
from pathlib import Path
from ctypes import c_char_p, c_void_p, c_int64

from .exceptions import (
    PlatformNotSupportedError,
    CoreLoadError,
    FileLockedError,
)


SUPPORTED_PLATFORMS = {
    ("windows", "x64"): "onewayswp_core.dll",
    ("windows", "arm64"): "onewayswp_core.dll",
    ("windows", "x86"): "onewayswp_core.dll",
    ("linux", "x64"): "libonewayswp_core.so",
    ("linux", "arm64"): "libonewayswp_core.so",
    ("linux", "armv7"): "libonewayswp_core.so",
    ("macos", "x64"): "libonewayswp_core.dylib",
    ("macos", "arm64"): "libonewayswp_core.dylib",
    ("android", "arm64"): "libonewayswp_core.so",
    ("android", "armv7"): "libonewayswp_core.so",
    ("android", "x64"): "libonewayswp_core.so",
    ("android", "x86"): "libonewayswp_core.so",
}


def detect_platform() -> tuple:
    system = platform.system().lower()
    machine = platform.machine().lower()

    if system == "windows":
        os_name = "windows"
    elif system == "darwin":
        os_name = "macos"
    elif system == "linux":
        if "android" in platform.platform().lower():
            os_name = "android"
        else:
            os_name = "linux"
    else:
        os_name = system

    if machine in ("x86_64", "amd64"):
        arch = "x64"
    elif machine in ("aarch64", "arm64"):
        arch = "arm64"
    elif machine.startswith("armv7") or machine == "armv7l":
        arch = "armv7"
    elif machine in ("i386", "i686", "x86"):
        arch = "x86"
    else:
        arch = machine

    return os_name, arch


def find_library() -> str:
    os_name, arch = detect_platform()
    key = (os_name, arch)

    if key not in SUPPORTED_PLATFORMS:
        supported = ", ".join(f"{o}-{a}" for o, a in sorted(SUPPORTED_PLATFORMS))
        raise PlatformNotSupportedError(
            f"Platform '{os_name}-{arch}' is not supported. Supported: {supported}"
        )

    lib_name = SUPPORTED_PLATFORMS[key]
    base = Path(__file__).parent / "lib"
    specific = base / f"{os_name}-{arch}" / lib_name

    if not specific.exists():
        raise CoreLoadError(
            f"Binary not found for {os_name}-{arch}. Expected at: {specific}"
        )

    return str(specific)


class CoreLib:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load()
        return cls._instance

    def _load(self) -> None:
        lib_path = find_library()

        try:
            loader = ctypes.WinDLL if platform.system() == "Windows" else ctypes.CDLL
            self.lib = loader(lib_path)
        except OSError as e:
            raise CoreLoadError(f"Failed to load core library: {e}")

        self.lib.owswp_version.restype = c_void_p
        self.lib.owswp_version.argtypes = []

        self.lib.owswp_info.restype = c_void_p
        self.lib.owswp_info.argtypes = []

        self.lib.owswp_generate_key_pair.restype = c_void_p
        self.lib.owswp_generate_key_pair.argtypes = []

        self.lib.owswp_validate_key_pair.restype = c_void_p
        self.lib.owswp_validate_key_pair.argtypes = [c_char_p, c_char_p]

        self.lib.owswp_create_license.restype = c_void_p
        self.lib.owswp_create_license.argtypes = [c_char_p, c_char_p, c_char_p]

        self.lib.owswp_validate_key.restype = c_void_p
        self.lib.owswp_validate_key.argtypes = [c_char_p, c_char_p, c_char_p]

        self.lib.owswp_inspect_key.restype = c_void_p
        self.lib.owswp_inspect_key.argtypes = [c_char_p, c_char_p]

        self.lib.owswp_protection_verify.restype = c_void_p
        self.lib.owswp_protection_verify.argtypes = [c_char_p, c_char_p]

        self.lib.owswp_decrement_credit.restype = c_void_p
        self.lib.owswp_decrement_credit.argtypes = [c_char_p, c_char_p, c_int64]

        self.lib.owswp_start_session.restype = c_void_p
        self.lib.owswp_start_session.argtypes = [c_char_p, c_char_p]

        self.lib.owswp_stop_session.restype = c_void_p
        self.lib.owswp_stop_session.argtypes = [c_char_p, c_char_p]

        self.lib.owswp_export_state.restype = c_void_p
        self.lib.owswp_export_state.argtypes = [c_char_p, c_char_p]

        self.lib.owswp_import_state.restype = c_void_p
        self.lib.owswp_import_state.argtypes = [c_char_p, c_char_p, c_char_p]

        self.lib.owswp_free_string.restype = None
        self.lib.owswp_free_string.argtypes = [c_void_p]

    def _call(self, func, *args) -> dict:
        encoded = [a.encode("utf-8") if isinstance(a, str) else a for a in args]
        ptr = func(*encoded)

        if not ptr:
            raise CoreLoadError("Core returned null pointer")

        try:
            raw = ctypes.cast(ptr, c_char_p).value
            if raw is None:
                raise CoreLoadError("Core returned empty response")
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as e:
            raise CoreLoadError(f"Invalid JSON from core: {e}")
        finally:
            self.lib.owswp_free_string(ptr)

    def version(self) -> dict:
        return self._call(self.lib.owswp_version)

    def info(self) -> dict:
        return self._call(self.lib.owswp_info)

    def generate_key_pair(self) -> dict:
        return self._call(self.lib.owswp_generate_key_pair)

    def validate_key_pair(self, secret: str, public: str) -> dict:
        return self._call(self.lib.owswp_validate_key_pair, secret, public)

    def create_license(self, secret: str, license_type: str, payload_json: str) -> dict:
        return self._call(self.lib.owswp_create_license, secret, license_type, payload_json)

    def validate_key(self, token: str, public: str, swpb_path: str) -> dict:
        return self._call(self.lib.owswp_validate_key, token, public, swpb_path)

    def inspect_key(self, token: str, public: str) -> dict:
        return self._call(self.lib.owswp_inspect_key, token, public)

    def protection_verify(self, public: str, swpb_path: str) -> dict:
        return self._call(self.lib.owswp_protection_verify, public, swpb_path)

    def decrement_credit(self, public: str, swpb_path: str, amount: int) -> dict:
        return self._call(self.lib.owswp_decrement_credit, public, swpb_path, amount)

    def start_session(self, public: str, swpb_path: str) -> dict:
        return self._call(self.lib.owswp_start_session, public, swpb_path)

    def stop_session(self, public: str, swpb_path: str) -> dict:
        return self._call(self.lib.owswp_stop_session, public, swpb_path)

    def export_state(self, public: str, swpb_path: str) -> dict:
        return self._call(self.lib.owswp_export_state, public, swpb_path)

    def import_state(self, public: str, swpb_path: str, data: str) -> dict:
        return self._call(self.lib.owswp_import_state, public, swpb_path, data)


_core_instance = None


def get_core() -> CoreLib:
    global _core_instance
    if _core_instance is None:
        _core_instance = CoreLib()
    return _core_instance


def retry_on_locked(func, *args, retries: int = 3, delay: float = 0.1, **kwargs):
    last_error = None
    for attempt in range(retries):
        try:
            return func(*args, **kwargs)
        except FileLockedError as e:
            last_error = e
            time.sleep(delay * (2 ** attempt))
    if last_error:
        raise last_error
    raise FileLockedError("File locked")