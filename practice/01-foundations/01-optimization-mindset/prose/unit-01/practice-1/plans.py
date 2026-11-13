from __future__ import annotations

from dataclasses import dataclass


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
    # TODO: add up the plan's value, and report every broken rule (see the statement's table).
    return -1, ["not checked yet"]


if __name__ == "__main__":
    demo = [Project("A", 50, 80, must_do=True), Project("B", 30, 40), Project("C", 20, 35, parent="B")]
    print(evaluate_plan(demo, 90, {"A", "C"}))
