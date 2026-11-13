"""A plan accepted with a binary 1e-6 from 0, and what rounding it does to the plan."""

from ortools.math_opt.python import mathopt

from gridcap import generate
from loan_model import EXACT, HUGE_M, NO_PRESOLVE, TIGHT, build, solve

small = generate("small")

best, _ = solve(build(small, TIGHT).model, params=EXACT)
lm = build(small, HUGE_M)
result, log = solve(lm.model, params=NO_PRESOLVE)
values = result.variable_values()

print(f"true optimum (tight M):         NPV less loan costs ${best.objective_value():,.1f}k")
print(f"M = 1e9, presolve off: {result.termination.reason.name}, NPV less loan costs ${result.objective_value():,.1f}k")
for y in small.years:
    take, loan = values[lm.take[y]], values[lm.loan[y]]
    if loan > 1e-6:
        spend = mathopt.evaluate_expression(lm.spend[y], values)
        print(f"  {y}: take = {take:.1e}  loan = ${loan:,.1f}k  M x take = {1e9 * take:,.1f}"
              f"  spend ${spend:,.0f}k, budget ${small.budget[y]:,}k")
print("HiGHS's report:", " | ".join(line.strip() for line in log if "viol." in line))

# Round every binary, as a planner reads the plan. A loan with take = 0 is not arranged, so it is 0.
rounded = {v: round(values[v]) for v in list(lm.x.values()) + list(lm.take.values())}
print("rounded plan:")
for y in small.years:
    spend = mathopt.evaluate_expression(lm.spend[y], rounded)
    loan = values[lm.loan[y]] if rounded[lm.take[y]] else 0.0
    if spend > small.budget[y] + loan:
        print(f"  {y}: spends ${spend:,.0f}k against a budget of ${small.budget[y]:,}k: over by ${spend - small.budget[y] - loan:,.0f}k")
paid = result.objective_value() - sum(300 for y in small.years if values[lm.loan[y]] > 1e-6 and not rounded[lm.take[y]])
print(f"keeping the loans and paying their fees instead: ${paid:,.1f}k")
