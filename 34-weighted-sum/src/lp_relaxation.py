"""The LP relaxation of the same question has no gap: its answer is reached by a weighted sum."""

from ortools.math_opt.python import mathopt

from gridcap import generate
from two_objectives import build, solve_highs

small = generate("small")
lp = build(small, integer=False)                     # every x[i, t] in [0, 1]


def value(lp, result) -> tuple[float, float]:
    x = result.variable_values()
    return (sum(lp.npv[k] * x[v] for k, v in lp.x.items()), sum(lp.rr[k] * x[v] for k, v in lp.x.items()))


floor = 23_104                                        # the NPV of the planners' plan in gridcap_frontier.py
row = lp.model.add_linear_constraint(lp.npv_of() >= floor, name="npv_floor")
lp.model.maximize(lp.risk_of())
result = solve_highs(lp.model)
npv, risk = value(lp, result)
x = result.variable_values()
fractional = sorted(k for k, v in lp.x.items() if 1e-6 < x[v] < 1 - 1e-6)
mu = -result.dual_values(row)                        # $k of risk the last $1k of NPV floor costs
print(f"LP, most risk with NPV >= ${floor:,}k: NPV ${npv:,.0f}k, risk ${risk:,.0f}k, "
      f"{len(fractional)} fractional starts, dual of the NPV floor {mu:.4f}")

lp.model.delete_linear_constraint(row)
lp.model.maximize(mu * lp.npv_of() + lp.risk_of())  # the weighted sum with price mu on NPV
best = solve_highs(lp.model).objective_value()
print(f"LP weighted sum, weights ({mu:.4f}, 1): optimum {best:,.1f}; "
      f"the epsilon answer scores {mu * npv + risk:,.1f}")
