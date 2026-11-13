from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

PLACES = 6          # decimals kept from every float: rates closer than a millionth are one rate


def fixed(value: float) -> float:
    """A float cut to PLACES decimals; NaN and infinity have no canonical form."""
    # TODO
    return value


def canonical(snap: dict) -> bytes:
    """One byte string per content: keys sorted at every level, no spaces, ASCII, no NaN."""
    # TODO
    return b""


def name(data: bytes) -> str:
    """The SHA-256 of some bytes, as 64 hex digits: the same bytes give the same name everywhere."""
    # TODO
    return ""


def digest(snap: dict) -> str:
    # TODO: the name of the canonical bytes.
    return ""


class Edited(Exception):
    """A stored file whose bytes no longer hash to its name."""


class Store:
    """Snapshots on disk, each written once as <digest>.json and re-hashed on every read."""

    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def put(self, snap: dict) -> str:
        """Write the canonical bytes once under their digest; return the digest."""
        # TODO
        return ""

    def get(self, key: str) -> dict:
        """Read a snapshot back; raise Edited if its bytes no longer hash to `key`."""
        # TODO
        return {}


if __name__ == "__main__":
    print(canonical({"rate": 0.0500000001, "years": [2027, 2028]}))
