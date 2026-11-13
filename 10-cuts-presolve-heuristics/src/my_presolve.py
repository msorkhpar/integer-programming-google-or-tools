"""Our own presolve on the five-year selection model, pass by pass, then postsolve and a check against HiGHS."""

from collections import Counter

from ortools.math_opt.python import mathopt

from gridcap import generate
from presolve import activity, from_selection, presolve, tighten, to_mathopt
from selection import five_year, plan_years, solve_quiet

EXACT = mathopt.SolveParameters(relative_gap_tolerance=0.0)   # prove the optimum, no 0.01% slack

medium = generate("medium")
full = five_year(medium)
original = from_selection(full.model)
print(f"original: {original.size()}")
kinds = Counter(name.split("_")[0] for name in original.rows)
print("  rows by kind: " + ", ".join(f"{k} {v}" for k, v in kinds.items()))

done = presolve(original)
for k, line in enumerate(done.log, start=1):
    print(f"pass {k}: {line}")
left = Counter(name.split("_")[0] for name in done.model.rows)
print("  rows left by kind: " + ", ".join(f"{k} {v}" for k, v in left.items()))
gone = [name for name in original.rows if name.startswith("budget") and name not in done.model.rows]
for name in gone:
    print(f"  {name} removed: the most it can hold is {activity(original.rows[name], original.lo, original.hi)[1]:,.0f}, "
          f"the budget {original.rows[name].rhs:,.0f}")
idle = [p for p in medium.projects if not set(p.spend(p.earliest_start)) & set(plan_years(medium))]
print(f"projects that spend nothing in {plan_years(medium)[0]}-{plan_years(medium)[-1]}: {len(idle)}; of them "
      f"{sum(p.must_do for p in idle)} must-do, {sum(bool(p.parent) for p in idle)} children, "
      f"{sum(bool(p.alt_group) for p in idle)} in an alternative group")
dual = [j for j, v in done.fixed.items() if not medium.project(j[2:]).must_do]
print(f"fixed without a must-do row: {len(dual)}, of which {sum(medium.project(j[2:]) in idle for j in dual)} spend nothing in those years")
ones = sum(v for v in done.fixed.values())
print(f"fixed {len(done.fixed)} variables: {ones} to 1, {len(done.fixed) - ones} to 0; "
      f"their value {done.constant:,.0f} is a constant now")

# Postsolve: solve the small model, then put the fixed values back.
model, x = to_mathopt(done.model)
small_result = solve_quiet(model, params=EXACT)
plan = dict(done.fixed)
plan.update({j: round(small_result.variable_values(v)) for j, v in x.items()})
value = sum(original.objective[j] * v for j, v in plan.items())
print(f"presolved model: {small_result.objective_value():,.0f} + constant {done.constant:,.0f} = {value:,.0f}")
breaks = [n for n, r in original.rows.items()
          if (lhs := sum(a * plan[j] for j, a in r.coefs.items())) > r.rhs + 1e-9 or (r.sense == "==" and lhs != r.rhs)]
print(f"the plan, put back together, breaks {len(breaks)} rows of the original model")
print(f"full model solved directly: {solve_quiet(full.model, params=EXACT).objective_value():,.0f}")

changes = [c for name, row in done.model.rows.items() for c in tighten(row, done.model.lo, done.model.hi)]
print(f"coefficient tightening changes {len(changes)} coefficients of the rows left")
