from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt


@dataclass(frozen=True)
class Project:
    pid: str
    cost: int
    value: int
    must_do: bool = False


def solve_plan(projects: list[Project], budget: int) -> tuple[str, float | None, frozenset[str] | None]:
    """Build the selection model, solve it with HiGHS, and read the answer status first."""
    # TODO: a model, one binary per project, the budget and must-do rows, the objective,
    # then mathopt.solve(..., mathopt.SolverType.HIGHS) and its status before any value.
    return "NOT_SOLVED", None, None


if __name__ == "__main__":
    demo = [Project("A", 50, 80, must_do=True), Project("B", 30, 40), Project("C", 20, 35)]
    print(solve_plan(demo, 90))
    print(solve_plan(demo, 40))
