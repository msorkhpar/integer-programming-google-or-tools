"""A constant added to the objective changes the relative gap, and with it where the solver stops."""

from ortools.math_opt.python import mathopt

from gridcap import generate
from selection import build, solve_highs

medium = generate("medium")
sel = build(medium)
npv = sum(p.value * sel.x[p.project_id] for p in medium.projects)

print(f"{'constant':>11} {'reason':<8} {'plan NPV':>9} {'gap':>5} {'rel gap seen':>12} {'rel gap on NPV':>14}")
for constant in (0, 2_000_000, 20_000_000):
    sel.model.maximize(npv + constant)
    result = solve_highs(sel.model, mathopt.SolveParameters(relative_gap_tolerance=1e-4))
    p = result.termination.objective_bounds.primal_bound
    d = result.termination.objective_bounds.dual_bound
    print(f"{constant:>11,} {result.termination.reason.name:<8} {p - constant:>9,.0f} {d - p:>5,.0f} "
          f"{(d - p) / p:>12.4%} {(d - p) / (p - constant):>14.4%}")
