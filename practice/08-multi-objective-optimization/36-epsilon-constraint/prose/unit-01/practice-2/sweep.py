from __future__ import annotations

from typing import Callable

Score = tuple[float, float]


def sweep(solve_at: Callable[[float], Score | None], low: float, high: float, n: int) -> list[Score]:
    """The different scores found at n evenly spaced floors from low to high, in the order found."""
    found: list[Score] = []
    # TODO: ask solve_at at each floor and keep each new score.
    return found


if __name__ == "__main__":
    plans = [(5200, 300.0), (4800, 420.0), (4100, 510.0)]          # (riders, tonnes cut)

    def solve_at(floor):
        meeting = [p for p in plans if p[1] >= floor]
        return max(meeting) if meeting else None

    print(sweep(solve_at, 300, 510, 4))
