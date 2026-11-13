"""Lesson 3.2.1: a general integer variable branches on floor and ceiling, not on 0 and 1.

A storm-hardening push hires whole contract crews: a line crews and b tree crews. A line crew
removes 5 risk points and a tree crew 8; there are 6 trucks, and a line crew costs $50k and a tree
crew $90k of a $450k budget.
"""

import math

from ortools.math_opt.python import mathopt

model = mathopt.Model(name="crews")
a = model.add_variable(lb=0, ub=6, name="a")
b = model.add_variable(lb=0, ub=6, name="b")
model.add_linear_constraint(a + b <= 6, name="trucks")
model.add_linear_constraint(50 * a + 90 * b <= 450, name="budget")
model.maximize(5 * a + 8 * b)
EPS = 1e-6


def solve(bounds: dict[str, tuple[float, float]]) -> tuple[float, dict[str, float]] | None:
    for var in (a, b):
        var.lower_bound, var.upper_bound = bounds[var.name]
    result = mathopt.solve(model, mathopt.SolverType.GLOP)
    if result.termination.reason == mathopt.TerminationReason.INFEASIBLE:
        return None
    return result.objective_value(), {v.name: result.variable_values(v) for v in (a, b)}


def children(bounds: dict, name: str, v: float) -> list[tuple[str, dict]]:
    """Down child: name <= floor(v). Up child: name >= ceil(v). Nothing strictly between is lost."""
    lo, hi = bounds[name]
    return [(f"{name} <= {math.floor(v)}", {**bounds, name: (lo, math.floor(v))}),
            (f"{name} >= {math.ceil(v)}", {**bounds, name: (math.ceil(v), hi)})]


def explore(bounds: dict, label: str, depth: int) -> None:
    solved = solve(bounds)
    if solved is None:
        print(f"{'  ' * depth}{label}: infeasible")
        return
    value, x = solved
    point = ", ".join(f"{n} = {v:g}" for n, v in x.items())
    split = [n for n, v in x.items() if abs(v - round(v)) > EPS]
    print(f"{'  ' * depth}{label}: LP {value:g} at ({point})" + ("" if split else "  integral"))
    if split:
        name = split[-1]
        for child_label, child in children(bounds, name, x[name]):
            explore(child, child_label, depth + 1)


explore({"a": (0, 6), "b": (0, 6)}, "root", 0)
