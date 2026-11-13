from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations


@dataclass(frozen=True)
class Project:
    pid: str
    cost: int
    value: int
    must_do: bool = False
    parent: str | None = None
    group: str | None = None


def evaluate_plan(projects: list[Project], budget: int, plan: set[str]) -> tuple[int, list[str]]:
    """Return the plan's total value and one problem string per rule it breaks."""
    # TODO: paste your evaluate_plan from the previous practice here, or write the checks again.
    return 0, ["not written yet"]


def cost(projects: list[Project], plan) -> int:
    return sum(p.cost for p in projects if p.pid in plan)


def best_plan(projects: list[Project], budget: int) -> tuple[int, frozenset[str]] | None:
    """The most valuable allowed plan, the cheaper one on a tie, or None if no plan is allowed."""
    # TODO: check every subset of the projects and keep the best allowed one.
    return (0, frozenset())


if __name__ == "__main__":
    demo = [Project("A", 50, 80, must_do=True), Project("B", 30, 40), Project("C", 20, 35, parent="B")]
    print(best_plan(demo, 90))
