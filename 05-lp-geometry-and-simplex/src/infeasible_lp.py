"""A commitment the budget cannot pay for: no plan satisfies every row, and the solvers say so."""

from ortools.math_opt.python import mathopt

from half_planes import broken
from split_lp import BOUNDS, ROWS, build
from vertices import vertices

COMMITTED = {**ROWS, "committed": ((-1, -1), -34)}   # d + t >= 34, written as -d - t <= -34


def total_violation(rows) -> float:
    """The phase-1 LP: give every row an elastic v_r >= 0, and find the least total stretch that fits a plan."""
    model = mathopt.Model(name="phase-one")
    d, t = model.add_variable(lb=0, name="d"), model.add_variable(lb=0, name="t")
    v = {label: model.add_variable(lb=0, name=f"v_{label}") for label in rows}
    for label, ((a_d, a_t), b) in rows.items():
        model.add_linear_constraint(a_d * d + a_t * t - v[label] <= b, name=label)
    model.minimize(sum(v.values()))
    return mathopt.solve(model, mathopt.SolverType.GLOP).objective_value()


if __name__ == "__main__":
    for d, t in [(12, 18), (10, 20), (24, 0), (20, 14)]:
        print(f"plan d={d:2}, t={t:2} breaks", ", ".join(broken(d, t, {**COMMITTED, **BOUNDS})))
    print("vertices of the region with the commitment:", len(vertices({**COMMITTED, **BOUNDS})))
    model, x = build(COMMITTED)
    for solver in (mathopt.SolverType.GLOP, mathopt.SolverType.HIGHS):
        print(f"{solver.name}: {mathopt.solve(model, solver).termination.reason.name}")
    print(f"least total violation without the commitment: {total_violation(ROWS):g}")
    print(f"least total violation with the commitment:    {total_violation(COMMITTED):g}")
