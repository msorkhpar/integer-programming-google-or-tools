"""What OPTIMAL meant: HiGHS and SCIP with their default tolerances, and HiGHS with a zero gap."""

from ortools.math_opt.python import mathopt

from gridcap import generate
from selection import build, plan, solve_highs

sel = build(generate("medium"))

log: list[str] = []
default = solve_highs(sel.model, mathopt.SolveParameters(enable_output=True), log=log)
scip = mathopt.solve(sel.model, mathopt.SolverType.GSCIP)
exact = solve_highs(sel.model, mathopt.SolveParameters(relative_gap_tolerance=0.0))

for name, r in (("HiGHS, defaults", default), ("SCIP, defaults", scip), ("HiGHS, zero gap", exact)):
    p, d = r.termination.objective_bounds.primal_bound, r.termination.objective_bounds.dual_bound
    print(f"{name:<16} {r.termination.reason.name}  incumbent {p:,.0f}  bound {d:,.0f}  "
          f"gap {d - p:,.0f} ({(d - p) / p:.4%})  nodes {r.solve_stats.node_count:,}")
print("HiGHS log, defaults:", [line.strip() for line in log if line.strip().startswith("Gap")][-1])
print(f"projects that differ, HiGHS defaults vs zero gap: {len(plan(sel, default) ^ plan(sel, exact))}")
