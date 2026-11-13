"""Search a grid of feasible points, then ask GLOP: neither beats the best vertex."""

import numpy as np
from ortools.math_opt.python import mathopt

from polygon import A, b, c, is_feasible

if __name__ == "__main__":
    grid = [np.array([d, v]) for d in range(0, 3001, 100) for v in range(0, 1501, 100)]
    inside = [p for p in grid if is_feasible(p)]
    top = max(c @ p for p in inside)
    winners = [tuple(p.tolist()) for p in inside if c @ p == top]
    print(f"grid: {len(grid)} points, {len(inside)} feasible, best objective {top:,} at {winners}")

    model = mathopt.Model(name="split-2028")
    d = model.add_variable(lb=0, name="d")
    v = model.add_variable(lb=0, name="v")
    for row, limit in zip(A, b):
        model.add_linear_constraint(float(row[0]) * d + float(row[1]) * v <= float(limit))
    model.maximize(float(c[0]) * d + float(c[1]) * v)
    result = mathopt.solve(model, mathopt.SolverType.GLOP)
    print(f"GLOP: {result.termination.reason.name}, (d, v) = ({result.variable_values(d):.0f},"
          f" {result.variable_values(v):.0f}), objective {result.objective_value():,.0f}")
