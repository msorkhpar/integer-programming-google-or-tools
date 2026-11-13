"""Lesson 10.2.3: how many plans fund the most projects on GridCap small? Count them with no-good rows.

GridCap is a fictional utility's portfolio. After each optimal plan is found, a no-good row forbids
exactly that plan, and the solve is repeated with the count held at its optimum.
"""

from ortools.math_opt.python import mathopt

from gridcap import generate
from plan_model import build, digest, schedule, solve_highs

EXACT = mathopt.SolveParameters(relative_gap_tolerance=0.0)
small = generate("small")
plan = build(small, objective="count")
best = round(solve_highs(plan.model, EXACT).objective_value())
plan.model.add_linear_constraint(sum(plan.x.values()) >= best, name="keep_count")

found = []
while len(found) < 20:
    result = solve_highs(plan.model, EXACT)
    if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
        break
    starts = schedule(plan, result)
    found.append(starts)
    chosen = [plan.x[pid, t] for pid, t in starts.items()]
    # no-good row: at least one of this plan's starts must be dropped
    plan.model.add_linear_constraint(sum(chosen) <= len(chosen) - 1, name=f"not_plan_{len(found)}")

print(f"most projects: {best}; distinct plans found with {best}: {len(found)} (search stopped at 20)")
a, b = found[0], found[1]
print("plan 1", digest(a), "NPV", f"{sum(small.project(i).npv[t] for i, t in a.items()):,}")
print("plan 2", digest(b), "NPV", f"{sum(small.project(i).npv[t] for i, t in b.items()):,}")
print("  only in plan 1:", sorted(set(a.items()) - set(b.items())))
print("  only in plan 2:", sorted(set(b.items()) - set(a.items())))

# The NPV question on the same data: is its best plan unique?
npv_plan = build(small)
first = solve_highs(npv_plan.model, EXACT)
top = round(first.objective_value())
starts = schedule(npv_plan, first)
npv_plan.model.add_linear_constraint(npv_plan.model.objective.as_linear_expression() >= top, name="keep_npv")
chosen = [npv_plan.x[k] for k in starts.items()]
npv_plan.model.add_linear_constraint(sum(chosen) <= len(chosen) - 1, name="not_this_plan")
again = solve_highs(npv_plan.model, EXACT)
print(f"highest NPV: {top:,} with plan {digest(starts)}; another plan with {top:,}: {again.termination.reason.name}")
