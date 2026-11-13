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
    seen = [canonical(run()) for _ in range(runs)]
    odd = next((k for k, m in enumerate(seen) if m != seen[0]), None)
    if odd is not None:
        fields = changed_fields(json.loads(seen[0]), json.loads(seen[odd]))
        raise AssertionError(f"run {odd + 1} of {runs} differs from run 1 in: {', '.join(fields)}")
    return hashlib.sha256(seen[0]).hexdigest()


if __name__ == "__main__":
    print(assert_deterministic(lambda: {"status": "OPTIMAL", "objective": 17.0}, 3))
