from __future__ import annotations

import hashlib
import json
import math

#: Lists whose order means nothing, with the field that sorts their records (None: sort the values).
UNORDERED = {"segments": "id", "tags": None}
PLACES = 3


def digest(doc: dict) -> str:
    """sha256 of the survey's canonical bytes."""
    # TODO: build the canonical form the statement describes, then hash it.
    return hashlib.sha256(json.dumps(doc).encode("utf-8")).hexdigest()


if __name__ == "__main__":
    print(digest({"version": 1, "tags": ["b", "a"], "rate": 0.05}))
