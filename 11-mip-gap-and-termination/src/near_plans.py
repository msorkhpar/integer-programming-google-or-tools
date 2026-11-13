"""Plans whose values are close can still pick different projects."""

from ortools.math_opt.python import mathopt

from gridcap import generate
from selection import build, plan, solve_highs

medium = generate("medium")
value = {p.project_id: p.value for p in medium.projects}
sel = build(medium)
exact = mathopt.SolveParameters(relative_gap_tolerance=0.0)

best_result = solve_highs(sel.model, exact)
best = plan(sel, best_result)
print(f"best plan: NPV {best_result.objective_value():,.0f}, {len(best)} projects")

loose = solve_highs(sel.model, mathopt.SolveParameters(relative_gap_tolerance=0.01))
found = plan(sel, loose)
print(f"stopped at 1%: NPV {loose.objective_value():,.0f}, adds {len(found - best)} projects "
      f"and drops {len(best - found)}")

# Every plan except the best one: at least one x[i] must differ from the best plan.
sel.model.add_linear_constraint(
    sum(sel.x[i] for i in best) - sum(sel.x[i] for i in sel.x if i not in best) <= len(best) - 1,
    name="not_the_best_plan")
runner_up = plan(sel, solve_highs(sel.model, exact))
print(f"second-best plan: NPV {sum(value[i] for i in runner_up):,}")
print(f"  adds    {sorted(runner_up - best)}, NPV {sum(value[i] for i in runner_up - best):,}")
print(f"  drops   {sorted(best - runner_up)}, NPV {sum(value[i] for i in best - runner_up):,}")
