from __future__ import annotations

import hashlib
import json


def snapshot_digest(inputs: dict) -> str:
    """sha256 hex digest of the inputs, the same for equal inputs in every process."""
    # TODO: write it.
    return "0" * 64


if __name__ == "__main__":
    print(snapshot_digest({"budget": {"2027": 4200}, "force_in": {"T-07", "T-11"}, "gap": 0.0}))
