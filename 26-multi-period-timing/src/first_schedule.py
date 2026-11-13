"""Solve the multi-period model on GridCap small and read the schedule out of x[i, t]."""

from ortools.math_opt.python import mathopt

from gridcap import generate
from timing_model import build, schedule

small = generate("small")
tm = build(small)
result = mathopt.solve(tm.model, mathopt.SolverType.HIGHS,
                       params=mathopt.SolveParameters(relative_gap_tolerance=0.0))
plan = schedule(tm, result)
print(result.termination.reason.name, f"NPV ${result.objective_value():,.0f}k")
late = {pid: t for pid, t in plan.items() if t > small.project(pid).earliest_start}
print(f"started {len(plan)} of {len(small.projects)}; {len(late)} later than their earliest year")
for pid, t in sorted(late.items()):
    p = small.project(pid)
    print(f"  {pid} window {p.earliest_start}-{p.latest_start} starts {t}  NPV {p.npv[p.earliest_start]:,} -> {p.npv[t]:,}")
by_year = {y: sum(1 for t in plan.values() if t == y) for y in small.years}
print("starts per year:", by_year)
