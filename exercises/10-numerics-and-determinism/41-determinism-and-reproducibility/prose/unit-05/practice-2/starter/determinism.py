from __future__ import annotations

import hashlib
import json


def canonical(manifest: dict) -> bytes:
    return json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")


def changed_fields(a: dict, b: dict) -> list[str]:
    """Top-level keys whose values differ, or that only one manifest has."""
    return sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))


def assert_deterministic(run, runs: int = 5) -> str:
    """Call run() `runs` times; return the manifest digest, or raise AssertionError naming the change."""
    # TODO: write it.
    return ""


if __name__ == "__main__":
    print(assert_deterministic(lambda: {"status": "OPTIMAL", "objective": 17.0}, 3))
