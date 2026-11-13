"""Lesson 2.3.1: the one-year LP, upper bounds from row prices, and the dual LP that finds the best one."""

from ortools.math_opt.python import mathopt

from budget_lp import value_per_k, work_per_crew_month
from gridcap import generate

tiny = generate("tiny")
YEAR = 2027
v, k = value_per_k(tiny), work_per_crew_month(tiny)
B = tiny.budget[YEAR]                                   # $k
D = k["distribution"] * tiny.crews["distribution", YEAR]  # $k of distribution work the crews can do
T = k["transmission"] * tiny.crews["transmission", YEAR]  # $k of transmission work the crews can do


def primal(budget: float = B) -> tuple[mathopt.Model, dict]:
    model = mathopt.Model(name="one-year")
    d = model.add_variable(lb=0, name="d")      # $k spent on distribution in 2027
    t = model.add_variable(lb=0, name="t")      # $k spent on transmission in 2027
    model.add_linear_constraint(d + t <= budget, name="budget")
    model.add_linear_constraint(d <= D, name="crew_d")
    model.add_linear_constraint(t <= T, name="crew_t")
    model.maximize(v["distribution"] * d + v["transmission"] * t)
    return model, {"d": d, "t": t}


def bound(y_budget: float, y_d: float, y_t: float) -> float | None:
    """The upper bound a price system proves, or None if the prices do not cover the objective."""
    nonnegative = min(y_budget, y_d, y_t) >= 0
    covers_d = y_budget + y_d >= v["distribution"]       # the d column: 1 in budget, 1 in crew_d
    covers_t = y_budget + y_t >= v["transmission"]       # the t column: 1 in budget, 1 in crew_t
    if not (nonnegative and covers_d and covers_t):
        return None
    return B * y_budget + D * y_d + T * y_t


def dual() -> tuple[mathopt.Model, dict]:
    model = mathopt.Model(name="one-year dual")
    y_budget = model.add_variable(lb=0, name="y_budget")
    y_d = model.add_variable(lb=0, name="y_crew_d")
    y_t = model.add_variable(lb=0, name="y_crew_t")
    model.add_linear_constraint(y_budget + y_d >= v["distribution"], name="cover_d")
    model.add_linear_constraint(y_budget + y_t >= v["transmission"], name="cover_t")
    model.minimize(B * y_budget + D * y_d + T * y_t)
    return model, {"budget": y_budget, "crew_d": y_d, "crew_t": y_t}


if __name__ == "__main__":
    print(f"value per $k: distribution {v['distribution']}, transmission {v['transmission']}")
    print(f"budget B = {B}, distribution crews D = {D}, transmission crews T = {T}")
    model, x = primal()
    result = mathopt.solve(model, mathopt.SolverType.GLOP)
    plan = {name: result.variable_values(var) for name, var in x.items()}
    print(f"primal: {result.termination.reason.name}, value {result.objective_value():,.1f}, plan {plan}")
    print()
    for prices in ((0.66, 0, 0), (0.5, 0.16, 0), (0.43, 0.23, 0), (0.43, 0, 0)):
        b = bound(*prices)
        print(f"prices {prices}: " + ("do not cover the objective" if b is None else f"bound {b:,.1f}"))
    print()
    model, y = dual()
    result = mathopt.solve(model, mathopt.SolverType.GLOP)
    prices = {name: round(result.variable_values(var), 4) for name, var in y.items()}
    print(f"dual:   {result.termination.reason.name}, value {result.objective_value():,.1f}, prices {prices}")
    print()
    base = mathopt.solve(primal()[0], mathopt.SolverType.GLOP).objective_value()
    for extra in (1, 100):
        more = mathopt.solve(primal(B + extra)[0], mathopt.SolverType.GLOP).objective_value()
        print(f"budget + {extra:>3}: value {more:,.2f}, up {more - base:,.2f}")
