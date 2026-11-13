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
    by_id = {p.pid: p for p in projects}
    chosen = [by_id[pid] for pid in plan]
    problems = []
    if sum(p.cost for p in chosen) > budget:
        problems.append("budget")
    problems += [f"must-do:{p.pid}" for p in projects if p.must_do and p.pid not in plan]
    problems += [f"parent:{p.pid}" for p in chosen if p.parent and p.parent not in plan]
    groups = [p.group for p in chosen if p.group]
    problems += [f"alternatives:{g}" for g in sorted(set(groups)) if groups.count(g) > 1]
    return sum(p.value for p in chosen), problems


if __name__ == "__main__":
    demo = [Project("A", 50, 80, must_do=True), Project("B", 30, 40), Project("C", 20, 35, parent="B")]
    print(evaluate_plan(demo, 90, {"A", "C"}))
