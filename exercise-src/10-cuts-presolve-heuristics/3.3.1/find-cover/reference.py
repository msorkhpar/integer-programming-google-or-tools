from __future__ import annotations

EPS = 1e-9


def find_cover(hours: dict[str, float], window: float, y: dict[str, float]) -> list[str] | None:
    """A minimal cover of the window row that the point y violates, or None if none is found."""
    order = sorted(hours, key=lambda j: ((1 - y[j]) / hours[j], j))
    cover, total = [], 0.0
    for j in order:
        cover.append(j)
        total += hours[j]
        if total > window:
            break
    else:
        return None
    for j in sorted(cover, key=lambda j: (-(1 - y[j]), j)):
        if sum(hours[k] for k in cover) - hours[j] > window:
            cover.remove(j)
    if sum(1 - y[j] for j in cover) < 1 - EPS:
        return cover
    return None


if __name__ == "__main__":
    print(find_cover({"J1": 5, "J2": 4, "J3": 3, "J4": 2}, 10, {"J1": 1, "J2": 1, "J3": 1 / 3, "J4": 0}))
