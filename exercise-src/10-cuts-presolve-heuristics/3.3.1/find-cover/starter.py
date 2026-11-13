from __future__ import annotations

EPS = 1e-9


def find_cover(hours: dict[str, float], window: float, y: dict[str, float]) -> list[str] | None:
    """A minimal cover of the window row that the point y violates, or None if none is found."""
    # TODO: take jobs in order of (1 - y_j) / a_j until their hours exceed the window; drop jobs,
    # the largest 1 - y_j first, while the set stays a cover; return it only if
    # sum of (1 - y_j) over it is below 1.
    return sorted(hours)


if __name__ == "__main__":
    print(find_cover({"J1": 5, "J2": 4, "J3": 3, "J4": 2}, 10, {"J1": 1, "J2": 1, "J3": 1 / 3, "J4": 0}))
