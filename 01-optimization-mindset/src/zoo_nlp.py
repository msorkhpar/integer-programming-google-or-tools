"""A nonlinear problem: split a budget across programs whose value shows diminishing returns."""

import math

from scipy.optimize import minimize

# value_k(s) = a_k * sqrt(s): each extra $k buys less than the one before.
A = {"transmission": 40.0, "distribution": 55.0, "vegetation": 25.0}
BUDGET = 7_390.0
programs = list(A)


def total_value(spend):
    return sum(A[k] * math.sqrt(max(s, 0.0)) for k, s in zip(programs, spend))


result = minimize(lambda s: -total_value(s), x0=[BUDGET / 3] * 3, method="SLSQP",
                  bounds=[(0, BUDGET)] * 3, constraints=[{"type": "eq", "fun": lambda s: sum(s) - BUDGET}])
print("SLSQP", "success" if result.success else "failed", f"value {total_value(result.x):,.1f}")
for k, s in zip(programs, result.x):
    print(f"  {k:13} ${s:,.0f}k")
