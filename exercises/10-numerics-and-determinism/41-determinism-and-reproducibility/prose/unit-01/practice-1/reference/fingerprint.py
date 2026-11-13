from __future__ import annotations

import hashlib
import json


def fingerprint(plan: dict[str, int]) -> str:
    """16 hex characters naming the plan: the same in every process, different for different plans."""
    text = json.dumps(sorted(plan.items()), separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


if __name__ == "__main__":
    print(fingerprint({"M07": 2028, "M12": 2027}))
