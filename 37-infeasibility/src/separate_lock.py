"""Lesson 9.1.1: two broken GridCap models that HiGHS reports alike, told apart; and a solve that cannot tell.

GridCap is a fictional utility's portfolio. The first model is the Budget Lock scenario (lock_model.LOCK).
The second has a modeling bug: finance's 3% interest on carried money, with each year's carry-over
added to the next year's cash but never taken out of its own year.
"""

import datetime

from ortools.math_opt.python import mathopt

from diagnose import runaway, separate, verdict
from gridcap import generate
from lock_model import LOCK, build, solve

small = generate("small")

base = build(small)
best = solve(base.model)
lock = build(small, LOCK)
print(f"base scenario: {best.termination.reason.name}, NPV ${best.objective_value():,.0f}k; "
      f"budget lock: {len(lock.x)} variables, {len(lock.rules)} rows")

bug = build(small)
carry = {y: bug.model.add_variable(lb=0, name=f"carry_{y}") for y in small.years}
for i, y in enumerate(small.years):
    bug.model.delete_linear_constraint(bug.rules[f"budget_{y}"])
    incoming = carry[small.years[i - 1]] if i else 0
    # The bug: + carry[y] is missing on the left, so money carried out of y never leaves y.
    bug.model.add_linear_constraint(bug.spend[y] <= small.budget[y] + incoming, name=f"cash_{y}")
bug.model.maximize(bug.npv + 0.03 * mathopt.fast_sum(carry.values()))

for name, model in (("budget lock", lock.model), ("carry bug", bug.model)):
    result = solve(model)
    print(f"{name:<12} HiGHS: {result.termination.reason.name:<24} separate(): {separate(model)}")
print("variables that run away:", runaway(bug.model))

medium = generate("medium")
rushed = solve(build(medium).model, params=mathopt.SolveParameters(time_limit=datetime.timedelta(milliseconds=1)))
print(f"medium, 1 ms: {rushed.termination.reason.name}, limit {rushed.termination.limit.name},"
      f" primal status {rushed.termination.problem_status.primal_status.name} -> {verdict(rushed)}")
