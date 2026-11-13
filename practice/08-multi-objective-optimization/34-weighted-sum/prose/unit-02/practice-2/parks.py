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
    # TODO: find the unbeaten plans, then one that no weighting picks, and its proof.
    return frozenset(), frozenset(), frozenset()


if __name__ == "__main__":
    park = [Project("trees", 7, 1, 10), Project("pond", 7, 4, 7), Project("courts", 8, 8, 6)]
    print(unreachable(park, 10))
