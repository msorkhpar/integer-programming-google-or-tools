from __future__ import annotations


def diff_paths(a, b, path: str = "") -> list[str]:
    """Sorted paths at which two manifests differ."""
    # TODO: write it.
    return []


if __name__ == "__main__":
    print(diff_paths({"result": {"objective": 41.0, "plan": [["S1", 3]]}},
                     {"result": {"objective": 41.0, "plan": [["S1", 4]]}}))
