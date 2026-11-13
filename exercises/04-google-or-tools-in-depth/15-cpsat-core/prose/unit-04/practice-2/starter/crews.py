from __future__ import annotations

from dataclasses import dataclass

from ortools.sat.python import cp_model


@dataclass(frozen=True)
class Job:
    name: str
    days: int      # days the job takes
    due: int       # the day it is due (lateness is measured from here)
    weight: int    # cost of one day of lateness


def best_order(jobs: list[Job]) -> tuple[int, list[str]]:
    """The least weighted lateness for one crew doing the jobs one at a time, and the order that gives it."""
    # TODO: start and lateness variables, one disjunction per pair, the objective; solve and read the order.
    return 0, [j.name for j in jobs]

if __name__ == "__main__":
    print(best_order([Job("north", 3, 4, 2), Job("ridge", 2, 2, 5), Job("creek", 4, 6, 1)]))
