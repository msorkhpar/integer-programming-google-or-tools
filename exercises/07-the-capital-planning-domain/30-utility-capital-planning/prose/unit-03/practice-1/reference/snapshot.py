from __future__ import annotations

import hashlib
import json

#: Fields that hold sets of project ids: their order means nothing.
UNORDERED = ("force_in", "force_out")


def canonical(inputs: dict) -> str:
    """One text for one set of inputs: sorted keys, sorted id lists, no spaces."""
    data = {k: sorted(v) if k in UNORDERED else v for k, v in inputs.items()}
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def snapshot_id(inputs: dict) -> str:
    return hashlib.sha256(canonical(inputs).encode("utf-8")).hexdigest()


def changed_fields(a: dict, b: dict) -> list[str]:
    """The top-level fields whose values differ between two scenarios' inputs, sorted."""
    return [k for k in sorted(set(a) | set(b))
            if k not in a or k not in b or canonical({k: a[k]}) != canonical({k: b[k]})]


if __name__ == "__main__":
    base = {"budget": {"2027": 900}, "force_in": ["W2", "W1"], "settings": {"gap": 0}}
    print(snapshot_id(base))
    print(changed_fields(base, {**base, "budget": {"2027": 800}}))
