from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations


@dataclass(frozen=True)
class Project:
    name: str
    cost: int          # $k
    shade: int         # square metres of tree canopy
    visits: int        # extra visits a week


def plans(projects: list[Project], budget: int) -> dict[frozenset[str], tuple[int, int]]:
    """Every set of projects the budget allows, with its (shade, visits)."""
    out = {}
    for size in range(len(projects) + 1):
        for chosen in combinations(projects, size):
            if sum(p.cost for p in chosen) <= budget:
                out[frozenset(p.name for p in chosen)] = (sum(p.shade for p in chosen),
                                                          sum(p.visits for p in chosen))
    return out


def unreachable(projects: list[Project], budget: int):
    """An unbeaten plan no weighting of shade and visits picks, with two plans that prove it.

    Returns (plan, a, b), three sets of project names: `plan` is dominated by no plan, and `a` and
    `b` are plans with less and more shade whose straight line passes strictly above `plan`. Returns
    None when every unbeaten plan is picked by some weighting.
    """
    scored = plans(projects, budget)
    by_point = {}
    for plan, point in sorted(scored.items(), key=lambda item: sorted(item[0])):
        by_point.setdefault(point, plan)
    front = sorted(p for p in by_point
                   if not any(o[0] >= p[0] and o[1] >= p[1] and o != p for o in by_point))
    hull = []
    for p in front:
        while len(hull) >= 2 and ((hull[-1][0] - hull[-2][0]) * (p[1] - hull[-2][1])
                                  - (hull[-1][1] - hull[-2][1]) * (p[0] - hull[-2][0])) > 0:
            hull.pop()
        hull.append(p)
    for q in front:
        if q in hull:
            continue
        a = max(h for h in hull if h[0] < q[0])
        b = min(h for h in hull if h[0] > q[0])
        return by_point[q], by_point[a], by_point[b]
    return None


if __name__ == "__main__":
    park = [Project("trees", 7, 1, 10), Project("pond", 7, 4, 7), Project("courts", 8, 8, 6)]
    print(unreachable(park, 10))
