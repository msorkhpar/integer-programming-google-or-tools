"""Check a plan and a price system against an LP without solving it (lesson 2.3.2).

The LP is a MathOpt maximization model whose variables are all >= 0 and whose rows are <=, >= or ==.
A plan maps each variable's name to its value; a price system maps each row's name to its price.
"""

import math

from ortools.math_opt.python import mathopt

TOL = 1e-6


def activity(row: mathopt.LinearConstraint, plan: dict[str, float]) -> float:
    """The row's left-hand side at the plan."""
    return sum(term.coefficient * plan[term.variable.name] for term in row.terms())


def rhs(row: mathopt.LinearConstraint) -> float:
    return row.upper_bound if row.upper_bound < math.inf else row.lower_bound


def slack(row: mathopt.LinearConstraint, plan: dict[str, float]) -> float:
    """How far the plan is from the row's limit: >= 0 when the row holds, 0 when it binds."""
    if row.upper_bound < math.inf and row.lower_bound > -math.inf:        # == row
        return -abs(activity(row, plan) - row.upper_bound)
    if row.upper_bound < math.inf:                                         # <= row
        return row.upper_bound - activity(row, plan)
    return activity(row, plan) - row.lower_bound                           # >= row


def plan_value(model: mathopt.Model, plan: dict[str, float]) -> float:
    return sum(model.objective.get_linear_coefficient(var) * plan[var.name] for var in model.variables())


def plan_is_feasible(model: mathopt.Model, plan: dict[str, float]) -> bool:
    return (all(plan[var.name] >= -TOL for var in model.variables())
            and all(slack(row, plan) >= -TOL for row in model.linear_constraints()))


def reduced_cost(model: mathopt.Model, var: mathopt.Variable, prices: dict[str, float]) -> float:
    """The variable's objective coefficient less the price of everything one unit of it uses."""
    used = sum(row.get_coefficient(var) * prices[row.name] for row in model.column_nonzeros(var))
    return model.objective.get_linear_coefficient(var) - used


def prices_are_feasible(model: mathopt.Model, prices: dict[str, float]) -> bool:
    """Dual feasible: each price has its row's sign, and no variable has a positive reduced cost."""
    for row in model.linear_constraints():
        y = prices[row.name]
        if row.lower_bound == -math.inf and y < -TOL:      # <= row needs y >= 0
            return False
        if row.upper_bound == math.inf and y > TOL:        # >= row needs y <= 0
            return False
    return all(reduced_cost(model, var, prices) <= TOL for var in model.variables())


def price_bound(model: mathopt.Model, prices: dict[str, float]) -> float | None:
    """The upper bound the prices prove (the dual objective), or None if they prove nothing."""
    if not prices_are_feasible(model, prices):
        return None
    return sum(rhs(row) * prices[row.name] for row in model.linear_constraints())
