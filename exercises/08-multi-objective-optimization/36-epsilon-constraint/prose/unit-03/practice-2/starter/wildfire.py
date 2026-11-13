from __future__ import annotations

Plan = tuple[float, float]          # (homes protected, budget left $k), both worth having


def upper_hull(points: list[Plan]) -> list[Plan]:
    """The supported plans: the upper-right convex hull of the frontier, fewest homes first.

    A plan exactly on the segment between two hull corners is kept: it is supported too.
    """
    hull: list[Plan] = []
    for p in sorted(points):
        while len(hull) >= 2:
            (x1, y1), (x2, y2) = hull[-2], hull[-1]
            if (x2 - x1) * (p[1] - y1) - (y2 - y1) * (p[0] - x1) > 0:
                hull.pop()                         # strictly below the segment to p
            else:
                break
        hull.append(p)
    return hull


def go_until(points: list[Plan], max_price: float) -> Plan:
    """The plan reached by taking every hull step priced at most `max_price` $k per home."""
    hull = upper_hull(points)
    at = (0.0, 0.0)
    # TODO: walk from the start of the hull, taking each step priced at most max_price.
    return at


if __name__ == "__main__":
    plans = [(100, 900), (140, 880), (150, 850), (200, 800), (210, 700), (260, 600)]
    print(go_until(plans, 2.0))
