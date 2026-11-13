"""Lesson 2.2.3: the two phases on a model the origin breaks but some plan satisfies."""

from ortools.math_opt.python import mathopt

from split_lp import BOUNDS, ROWS, build
from vertices import vertices

FLOOR = {**ROWS, "floor": ((-1, -1), -20)}   # d + t >= 20, written as -d - t <= -20; (0, 0) breaks it


def phase_one(rows) -> tuple[float, float, float]:
    """The phase-1 LP: least total stretch, and the plan (d, t) it ends at."""
    model = mathopt.Model(name="phase-one")
    d, t = model.add_variable(lb=0, name="d"), model.add_variable(lb=0, name="t")
    v = {label: model.add_variable(lb=0, name=f"v_{label}") for label in rows}
    for label, ((a_d, a_t), b) in rows.items():
        model.add_linear_constraint(a_d * d + a_t * t - v[label] <= b, name=label)
    model.minimize(sum(v.values()))
    result = mathopt.solve(model, mathopt.SolverType.GLOP)
    return result.objective_value(), result.variable_values(d) + 0.0, result.variable_values(t) + 0.0


if __name__ == "__main__":
    stretch, d, t = phase_one(FLOOR)
    corners = vertices({**FLOOR, **BOUNDS})
    print(f"phase 1: least total stretch {stretch:g}, at plan ({d:g}, {t:g})")
    print(f"is ({d:g}, {t:g}) a vertex of the original region? {(d, t) in corners}; "
          f"rows tight there: {', '.join(corners.get((d, t), []))}")
    model, x = build(FLOOR)
    result = mathopt.solve(model, mathopt.SolverType.GLOP)
    print(f"the optimum phase 2 walks to (solved here by GLOP): {result.termination.reason.name}, "
          f"d = {result.variable_values(x['d']):g}, t = {result.variable_values(x['t']):g}, "
          f"value = {result.objective_value():g}")
