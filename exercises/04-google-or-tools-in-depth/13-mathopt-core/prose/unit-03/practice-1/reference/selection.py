from __future__ import annotations

import pandas as pd
from ortools.math_opt.python import mathopt

LP_ONLY = (mathopt.SolverType.GLOP, mathopt.SolverType.PDLP)


def solve_selection(df: pd.DataFrame, budget: float, solver: mathopt.SolverType) -> tuple[float, list[str]]:
    """The best plan's value and its sorted project ids, on any MILP solver MathOpt drives."""
    if solver in LP_ONLY:
        raise ValueError(f"{solver.name} solves LPs only; this model has yes/no variables")
    model = mathopt.Model(name="selection")
    x = {row.project_id: model.add_binary_variable(name=f"x_{row.project_id}") for row in df.itertuples()}
    model.add_linear_constraint(
        mathopt.fast_sum(row.cost * x[row.project_id] for row in df.itertuples()) <= budget, name="budget")
    for row in df.itertuples():
        if row.must_do:
            model.add_linear_constraint(x[row.project_id] == 1, name=f"must_{row.project_id}")
    model.maximize(mathopt.fast_sum(row.value * x[row.project_id] for row in df.itertuples()))
    result = mathopt.solve(model, solver)
    if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
        raise RuntimeError(f"no optimal plan: {result.termination.reason.name}")
    chosen = sorted(pid for pid, var in x.items() if result.variable_values(var) > 0.5)
    return result.objective_value(), chosen


if __name__ == "__main__":
    parks = pd.DataFrame({"project_id": ["A", "B", "C"], "cost": [40, 30, 50],
                          "value": [55, 35, 60], "must_do": [False, True, False]})
    print(solve_selection(parks, 80, mathopt.SolverType.HIGHS))
