from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations


@dataclass(frozen=True)
class Project:
    pid: str
    cost: int
    must_do: bool = False
    parent: str | None = None
    group: str | None = None


def allowed(plan: set[str], projects: list[Project], budget: int) -> bool:
    """True if the plan keeps the budget, must-do, parent and alternative rows."""
    # TODO: check each row.
    return False


def count_allowed(projects: list[Project], budget: int) -> int:
    """How many of the 2^n plans keep every rule, checking each one."""
    # TODO: go through every subset of the project ids, including the empty one.
    return 0


if __name__ == "__main__":
    bays = [Project("M", 40, must_do=True), Project("A", 30), Project("B", 20, group="G"), Project("C", 25, group="G")]
    print(count_allowed(bays, 100))
