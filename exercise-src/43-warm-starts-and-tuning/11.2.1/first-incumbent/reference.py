from __future__ import annotations

import math

# Each event is (work, objective): the solver's deterministic work when it found a plan, and that plan's cost.
Event = tuple[float, float]


def work_to_first(events: list[Event]) -> float:
    """The work at which the first plan was found, or infinity if none was."""
    return min((work for work, _ in events), default=math.inf)


def work_to_within(events: list[Event], best: float, share: float) -> float:
    """The work until a plan costing at most `best` plus `share` of |best| was found (a minimization)."""
    target = best + share * abs(best)
    return min((work for work, cost in events if cost <= target), default=math.inf)


def in_hand(events: list[Event], budget: float) -> float | None:
    """The cheapest plan found with at most `budget` work, or None if none was found by then."""
    return min((cost for work, cost in events if work <= budget), default=None)


if __name__ == "__main__":
    log = [(0.0, 1300.0), (40.0, 1180.0), (40.0, 1210.0), (300.0, 1010.0)]
    print(work_to_first(log), work_to_within(log, 1000.0, 0.02), in_hand(log, 100.0))
