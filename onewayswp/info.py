from ._core import get_core


class _Info:
    def __init__(self) -> None:
        self._data: dict = {}
        self._loaded: bool = False

    def _load(self) -> dict:
        if not self._loaded:
            response = get_core().info()
            if response.get("status"):
                self._data = {
                    k: v
                    for k, v in response.items()
                    if k not in ("status", "code", "message")
                }
            self._loaded = True
        return self._data

    def __getattr__(self, name: str):
        data = self._load()
        if name in data:
            return data[name]
        raise AttributeError(f"'info' has no attribute '{name}'")

    def __getitem__(self, key: str):
        return self._load().get(key)

    def __contains__(self, key: str) -> bool:
        return key in self._load()

    def __iter__(self):
        return iter(self._load())

    def __len__(self) -> int:
        return len(self._load())

    def keys(self):
        return self._load().keys()

    def values(self):
        return self._load().values()

    def items(self):
        return self._load().items()

    def get(self, key: str, default=None):
        return self._load().get(key, default)

    def to_dict(self) -> dict:
        return dict(self._load())

    def __repr__(self) -> str:
        return f"info({self._load()})"

    def __str__(self) -> str:
        data = self._load()
        lines = ["OnewaySWP Library Info", "=" * 40]
        for k, v in data.items():
            if k == "description":
                lines.append(f"{k}:")
                lines.append(f"  {v}")
            else:
                lines.append(f"{k}: {v}")
        return "\n".join(lines)


info = _Info()