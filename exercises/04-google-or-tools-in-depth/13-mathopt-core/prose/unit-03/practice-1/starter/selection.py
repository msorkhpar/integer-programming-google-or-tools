from __future__ import annotations

import pandas as pd
from ortools.math_opt.python import mathopt

LP_ONLY = (mathopt.SolverType.GLOP, mathopt.SolverType.PDLP)


def solve_selection(df: pd.DataFrame, budget: float, solver: mathopt.SolverType) -> tuple[float, list[str]]:
    """The best plan's value and its sorted project ids, on any MILP solver MathOpt drives."""
    # TODO: refuse LP-only solvers, build the model, solve with `solver`, check the reason, read the plan.
    return 0.0, []


if __name__ == "__main__":
    parks = pd.DataFrame({"project_id": ["A", "B", "C"], "cost": [40, 30, 50],
                          "value": [55, 35, 60], "must_do": [False, True, False]})
    print(solve_selection(parks, 80, mathopt.SolverType.HIGHS))
