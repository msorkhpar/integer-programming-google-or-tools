"""Slack and surplus: turn each inequality into an equation with one extra variable >= 0."""

import math

from ortools.math_opt.python import mathopt

from gridcap import PROGRAMS
from program_split import CREW, FLOOR, SHARE, VALUE, activity, build, small

YEAR = 2027


def equality_form():
    """The split LP with every row an equation: a slack on each <= row, a surplus on each >= row."""
    model = mathopt.Model(name="program split, equality form")
    s = {k: model.add_variable(lb=0, name=f"s_{k}") for k in PROGRAMS}
    extra = {}

    def row(expr, sense: str, rhs: float, name: str) -> None:
        extra[name] = model.add_variable(lb=0, name=f"{'slack' if sense == '<=' else 'surplus'}_{name}")
        if sense == "<=":
            model.add_linear_constraint(expr + extra[name] == rhs, name=name)      # a.x + slack = b
        else:
            model.add_linear_constraint(expr - extra[name] == rhs, name=name)      # a.x - surplus = b

    row(sum(s.values()), "<=", small.budget[YEAR], "budget")
    for k in PROGRAMS:
        row(CREW[k] / 1000 * s[k], "<=", small.crews[k, YEAR], f"crew_{k}")
    for k, amount in FLOOR.items():
        row(s[k], ">=", amount, f"floor_{k}")
    for k in PROGRAMS:
        row(s[k] - SHARE * sum(s.values()), "<=", 0, f"share_{k}")
    model.maximize(sum(VALUE[k] * s[k] for k in PROGRAMS))
    return model, extra


if __name__ == "__main__":
    model, extra = equality_form()
    result = mathopt.solve(model, mathopt.SolverType.GLOP)
    print(f"equality form: {result.termination.reason.name}, NPV {result.objective_value():,.1f}")
    split = build(YEAR)
    check = mathopt.solve(split.model, mathopt.SolverType.GLOP)
    print(f"{'row':20} {'variable':30} {'solver value':>12} {'room':>10}")
    for name, var in extra.items():
        row = split.rows[name]
        room = row.upper_bound - activity(row, check) if math.isfinite(row.upper_bound) \
            else activity(row, check) - row.lower_bound
        room = 0.0 if abs(room) < 1e-9 else room                        # print 0.0, not -0.0
        print(f"{name:20} {var.name:30} {result.variable_values(var):12,.1f} {room:10,.1f}")
