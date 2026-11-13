"""How much work each solver spends to reach a gap target, and what each one's default target is (lesson 5.4.2).

Time-to-gap measured in each solver's deterministic unit, so the numbers repeat: the same instance,
seed 1, one thread, stopped at relative gap targets of 5%, 1%, 0.1% and 0. The gap printed is the
harness's own, |bound - objective| / |objective|, the same for every solver.
"""

from __future__ import annotations

from ortools.math_opt.python import mathopt

from instances import build_mathopt, instance_set
from quiet import muted
from solvers import MEASURES, run

TARGETS = (0.05, 0.01, 0.001, 0.0)

inst = next(i for i in instance_set() if i.name == "distribution-2027")
print(f"instance {inst.name}: {len(inst.projects)} projects, seed 1, one thread")
print(f"{'solver':<7} {'target':>7} {'objective':>10} {'bound':>10} {'gap':>8} {'work':>10}  share of work to optimal")
for solver in ("HiGHS", "SCIP", "CP-SAT", "CBC"):
    unit = MEASURES[solver][0]
    runs = [run(solver, inst, 1, gap=g) for g in TARGETS]
    full = runs[-1].work[unit]
    for g, r in zip(TARGETS, runs):
        print(f"{solver:<7} {g:>7.1%} {r.objective:>10,.0f} {r.bound:>10,.1f} {r.gap():>8.4%} "
              f"{r.work[unit]:>10g}  {r.work[unit] / full:>6.1%} of {full:g} {unit}")

print("\nwith no gap target set (each solver's own default), through MathOpt:")
model, _ = build_mathopt(inst)
for name, kind in (("HiGHS", mathopt.SolverType.HIGHS), ("SCIP", mathopt.SolverType.GSCIP),
                   ("CP-SAT", mathopt.SolverType.CP_SAT)):
    with muted():
        result = mathopt.solve(model, kind)
    obj, bound = result.objective_value(), result.termination.objective_bounds.dual_bound
    print(f"  {name:<7} {result.termination.reason.name:<8} objective {obj:,.0f}  bound {bound:,.1f}  "
          f"gap {abs(bound - obj) / abs(obj):.4%}")
