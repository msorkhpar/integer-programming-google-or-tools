"""Mock 4's traps about prices: binding rows with a zero price, a MILP with no duals, and the
fixed-integer re-solve of an all-binary model.

The models are made up for the question and small enough to check by hand.
"""

from __future__ import annotations

from ortools.math_opt.python import mathopt

from mock_support import quiet_solve


def degenerate_lp() -> None:
    """max x + y with x <= 1, y <= 1 and x + y <= 2: three rows meet at one vertex in two dimensions."""
    model = mathopt.Model(name="degenerate")
    x = model.add_variable(lb=0, name="x")
    y = model.add_variable(lb=0, name="y")
    rows = [model.add_linear_constraint(x <= 1, name="cap_x"),
            model.add_linear_constraint(y <= 1, name="cap_y"),
            model.add_linear_constraint(x + y <= 2, name="total")]
    model.maximize(x + y)
    result = mathopt.solve(model, mathopt.SolverType.GLOP)
    print(f"degenerate LP: {result.termination.reason.name}, objective {result.objective_value():g}")
    for row in rows:
        activity = sum(result.variable_values(v) * c for v, c in [(x, row.get_coefficient(x)), (y, row.get_coefficient(y))])
        print(f"  {row.name:<6} slack {row.upper_bound - activity:g}  price {result.dual_values(row):g}")


def knapsack(fixed: dict | None = None) -> tuple[mathopt.Model, dict, mathopt.LinearConstraint]:
    model = mathopt.Model(name="three-projects")
    value, cost = {"P1": 60, "P2": 50, "P3": 40}, {"P1": 30, "P2": 20, "P3": 20}
    x = {p: model.add_binary_variable(name=f"x_{p}") for p in value}
    budget = model.add_linear_constraint(sum(cost[p] * x[p] for p in x) <= 50, name="budget")
    model.maximize(sum(value[p] * x[p] for p in x))
    return model, x, budget


def milp_has_no_duals() -> dict:
    model, x, budget = knapsack()
    result = quiet_solve(model)
    plan = {p: round(result.variable_values(v)) for p, v in x.items()}
    print(f"MILP: {result.termination.reason.name}, objective {result.objective_value():g}, plan {plan}")
    print(f"  has_dual_feasible_solution(): {result.has_dual_feasible_solution()}")
    try:
        result.dual_values(budget)
    except ValueError as error:
        print(f"  dual_values(budget) raises ValueError: {error}")
    return plan


def fixed_integer_resolve(plan: dict) -> None:
    model, x, budget = knapsack()
    for p, var in x.items():                   # fix each binary at its value and drop integrality
        var.lower_bound = var.upper_bound = plan[p]
        var.integer = False
    result = mathopt.solve(model, mathopt.SolverType.GLOP)
    print(f"fixed-integer LP: {result.termination.reason.name}, objective {result.objective_value():g}")
    print(f"  budget price {result.dual_values(budget):g}; reduced costs "
          + ", ".join(f"{p} {result.reduced_costs(v):g}" for p, v in x.items()))


def main() -> None:
    degenerate_lp()
    print()
    plan = milp_has_no_duals()
    print()
    fixed_integer_resolve(plan)


if __name__ == "__main__":
    main()
