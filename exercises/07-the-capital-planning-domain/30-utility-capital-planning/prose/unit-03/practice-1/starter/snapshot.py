from __future__ import annotations

import hashlib
import json

#: Fields that hold sets of project ids: their order means nothing.
UNORDERED = ("force_in", "force_out")


def snapshot_id(inputs: dict) -> str:
    # TODO: hash one canonical text of the inputs. The empty string is a placeholder.
    return ""


def changed_fields(a: dict, b: dict) -> list[str]:
    """The top-level fields whose values differ between two scenarios' inputs, sorted."""
    # TODO: compare the two scenarios field by field. The empty list is a placeholder.
    return []


if __name__ == "__main__":
    base = {"budget": {"2027": 900}, "force_in": ["W2", "W1"], "settings": {"gap": 0}}
    print(snapshot_id(base))
    print(changed_fields(base, {**base, "budget": {"2027": 800}}))
