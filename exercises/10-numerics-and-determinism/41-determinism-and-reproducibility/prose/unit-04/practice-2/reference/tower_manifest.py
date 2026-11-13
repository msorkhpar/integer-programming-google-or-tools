from __future__ import annotations

import json

LEFT_OUT = {"started_at", "wall_seconds", "host"}


def manifest_bytes(record: dict) -> bytes:
    """The canonical manifest of a run record, as bytes."""
    manifest = {k: v for k, v in record.items() if k not in LEFT_OUT}
    return json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")


if __name__ == "__main__":
    print(manifest_bytes({"inputs_digest": "9f2c", "solver": "highs", "params": {}, "versions": {},
                          "status": "OPTIMAL", "objective": 812.0, "plan": {"TW-12": 2027},
                          "started_at": "2026-11-11T02:00:03", "wall_seconds": 41.7, "host": "batch-node-7"}))
