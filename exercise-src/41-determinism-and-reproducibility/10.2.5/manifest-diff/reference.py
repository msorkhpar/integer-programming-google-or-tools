from __future__ import annotations

MISSING = object()


def join(path: str, key) -> str:
    return f"{path}.{key}" if path else str(key)


def diff_paths(a, b, path: str = "") -> list[str]:
    """Sorted paths at which two manifests differ."""
    if isinstance(a, dict) and isinstance(b, dict):
        pairs = [(join(path, k), a.get(k, MISSING), b.get(k, MISSING)) for k in a.keys() | b.keys()]
    elif isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        pairs = [(f"{path}[{i}]", x, y) for i, (x, y) in enumerate(zip(a, b))]
    else:
        return [path] if a != b else []
    out = []
    for where, x, y in pairs:
        out += [where] if x is MISSING or y is MISSING else diff_paths(x, y, where)
    return sorted(out)


if __name__ == "__main__":
    print(diff_paths({"result": {"objective": 41.0, "plan": [["S1", 3]]}},
                     {"result": {"objective": 41.0, "plan": [["S1", 4]]}}))
