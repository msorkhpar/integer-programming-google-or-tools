"""Yes/no decisions make the set of plans non-convex, and the LP's best corner can be fractional."""

import numpy as np
from ortools.math_opt.python import mathopt

from all_plans import X, feasible
from gridcap import generate
from rules_matrix import full_model

tiny = generate("tiny")
ids = tiny.project_ids
names, A, b = full_model()
npv = [p.value for p in tiny.projects]


def lp_relaxation() -> tuple[str, float, dict[str, float]]:
    model = mathopt.Model(name="tiny-yearly-lp")
    x = [model.add_variable(lb=0, ub=1, name=f"x_{pid}") for pid in ids]
    for name, row, limit in zip(names, A, b):
        model.add_linear_constraint(
            expr=mathopt.LinearExpression(sum(float(a) * xj for a, xj in zip(row, x) if a)),
            ub=float(limit), name=name)
    model.maximize(sum(float(v) * xj for v, xj in zip(npv, x)))
    result = mathopt.solve(model, mathopt.SolverType.GLOP)
    values = {pid: round(result.variable_values(xj), 3) for pid, xj in zip(ids, x)}
    return result.termination.reason.name, result.objective_value(), values


if __name__ == "__main__":
    plans = X[:, feasible]
    p, q = plans[:, 1], plans[:, 2]
    mid = (p + q) / 2
    print("plan p :", p)
    print("plan q :", q)
    print("middle :", mid)
    print("middle satisfies A x <= b:", bool(np.all(A @ mid <= b)))
    print("middle is a plan (all 0 or 1):", bool(np.all((mid == 0) | (mid == 1))))
    status, value, values = lp_relaxation()
    print(f"LP relaxation: {status}, value {value:,.1f}")
    print("  ", {pid: v for pid, v in values.items() if v > 0})
