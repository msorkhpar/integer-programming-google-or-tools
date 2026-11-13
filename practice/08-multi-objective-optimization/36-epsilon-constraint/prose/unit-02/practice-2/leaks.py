from __future__ import annotations

import math


def exact_sweep(solve_at, low: int, high: int, step: int = 1) -> list[tuple[float, int]]:
    """Every plan, from the highest cost ceiling down, skipping ceilings the slack covers."""
    plans, ceiling = [], high
    # TODO: ask, keep the plan, jump past the ceilings its slack covers; stop at the first None.
    return plans


if __name__ == "__main__":
    frontier = [(870.0, 100), (900.0, 112), (950.0, 130)]       # (leak cut, cost $k)

    def solve_at(ceiling):
        within = [p for p in frontier if p[1] <= ceiling]
        return (max(within), ceiling - max(within)[1]) if within else None

    print(exact_sweep(solve_at, 90, 130))
