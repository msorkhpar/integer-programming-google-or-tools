from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

PLACES = 6          # decimals kept from every float: rates closer than a millionth are one rate


def fixed(value: float) -> float:
    """A float cut to PLACES decimals; NaN and infinity have no canonical form."""
    if not math.isfinite(value):
        raise ValueError(f"{value!r} has no canonical form")
    return float(f"{value:.{PLACES}f}") + 0.0


def plain(value):
    """The snapshot as JSON-ready data with every float fixed; lists keep their order."""
    if isinstance(value, bool) or value is None or isinstance(value, (int, str)):
        return value
    if isinstance(value, float):
        return fixed(value)
    if isinstance(value, dict):
        return {k: plain(v) for k, v in value.items()}
    return [plain(v) for v in value]


def canonical(snap: dict) -> bytes:
    """One byte string per content: keys sorted at every level, no spaces, ASCII, no NaN."""
    return json.dumps(plain(snap), sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                      allow_nan=False).encode("ascii")


def name(data: bytes) -> str:
    """The SHA-256 of some bytes, as 64 hex digits: the same bytes give the same name everywhere."""
    return hashlib.sha256(data).hexdigest()


def digest(snap: dict) -> str:
    return name(canonical(snap))


class Edited(Exception):
    """A stored file whose bytes no longer hash to its name."""


class Store:
    """Snapshots on disk, each written once as <digest>.json and re-hashed on every read."""

    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def put(self, snap: dict) -> str:
        data = canonical(snap)
        key = name(data)
        path = self.root / f"{key}.json"
        if not path.exists():
            path.write_bytes(data)
        return key

    def get(self, key: str) -> dict:
        data = (self.root / f"{key}.json").read_bytes()
        if name(data) != key:
            raise Edited(f"{key[:12]}.json was edited")
        return json.loads(data)


if __name__ == "__main__":
    print(canonical({"rate": 0.0500000001, "years": [2027, 2028]}))
