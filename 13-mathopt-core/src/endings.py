"""Six ways a solve can end, and what each result does and does not carry."""

import dataclasses

from ortools.math_opt.python import mathopt

from gridcap import generate
from selection import build, solve

S = mathopt.SolverType
small = generate("small")


def unbounded_lp() -> mathopt.Model:
    """max x + y with y - x <= 2, 0 <= y <= 5 and x >= 0 with no upper bound: x can grow forever."""
    model = mathopt.Model(name="no-upper-bound")
    x = model.add_variable(lb=0, name="x")
    y = model.add_variable(lb=0, ub=5, name="y")
    model.add_linear_constraint(y - x <= 2, name="r")
    model.maximize(x + y)
    return model


cases = [
    ("GridCap small, HiGHS", build(small).model, S.HIGHS, None),
    ("solution_limit=1, HiGHS", build(small).model, S.HIGHS, mathopt.SolveParameters(solution_limit=1)),
    ("iteration_limit=1, LP, HiGHS", build(small, integer=False).model, S.HIGHS,
     mathopt.SolveParameters(iteration_limit=1)),
    ("budgets of $100k, HiGHS", build(dataclasses.replace(small, budget={y: 100 for y in small.years})).model,
     S.HIGHS, None),
    ("x unbounded, HiGHS", unbounded_lp(), S.HIGHS, None),
    ("x unbounded, GLOP", unbounded_lp(), S.GLOP, None),
]

for label, model, solver, params in cases:
    result = solve(model, solver, params)
    term = result.termination
    status = term.problem_status
    try:
        value = f"{result.objective_value():,.1f}"
    except ValueError:
        value = "ValueError"
    limit = term.limit.name if term.limit else "-"
    print(f"{label}")
    print(f"  {term.reason.name:<23} limit {limit:<9} primal/dual status {status.primal_status.name}/{status.dual_status.name}")
    print(f"  has plan {result.has_primal_feasible_solution()!s:<5}  objective_value {value:<10}"
          f"  primal_bound {result.primal_bound():,.1f}  dual_bound {result.dual_bound():,.1f}")
