from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt


@dataclass(frozen=True)
class Project:
    pid: str
    cost: int
    value: int
    parent: str | None = None


def solve(projects: list[Project], budget: int, integer: bool) -> float:
    """The selection model's optimal value: the MILP with HiGHS, or its LP relaxation with GLOP."""
    # TODO: one variable per project with the domain `integer` asks for, the budget and parent
    # rows, the objective, then solve with HiGHS (integer) or GLOP (relaxation).
    return 0.0


def integrality_gap(projects: list[Project], budget: int) -> tuple[float, float, float]:
    """(LP bound, best plan's value, integrality gap as a share of the best plan's value)."""
    # TODO: solve the relaxation and the MILP, then compute the gap.
    return 0.0, 0.0, 0.0


if __name__ == "__main__":
    yards = [Project("A", 60, 66), Project("B", 50, 60), Project("C", 40, 36)]
    print(integrality_gap(yards, 100))
    linked = [Project("P", 50, 40), Project("Q", 40, 64, parent="P"), Project("R", 30, 30)]
    print(integrality_gap(linked, 100))
