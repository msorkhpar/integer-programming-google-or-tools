from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Problem:
    routes: bool = False
    shape: str | None = None          # "assignment", "flow", "knapsack" or None
    side_rules: bool = False
    continuous: bool = False
    needs_duals: bool = False
    intervals: bool = False
    logic: bool = False


def choose_api(problem: Problem) -> str:
    """'routing', 'graph', 'knapsack', 'CP-SAT' or 'MathOpt', by the five questions in order."""
    if problem.routes:
        return "routing"
    if problem.shape is not None and not problem.side_rules:
        return "knapsack" if problem.shape == "knapsack" else "graph"
    if problem.continuous or problem.needs_duals:
        return "MathOpt"
    if problem.intervals or problem.logic:
        return "CP-SAT"
    return "MathOpt"


if __name__ == "__main__":
    print(choose_api(Problem(shape="assignment", side_rules=True)))
