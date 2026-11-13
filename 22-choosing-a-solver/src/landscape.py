"""The four MILP solvers the course runner has, on one GridCap instance: same answer, different reports (lesson 5.4.1)."""

from __future__ import annotations

from instances import build_wrapper, instance_set
from solvers import MEASURES, TAKES_SEED, run

inst = next(i for i in instance_set() if i.name == "transmission-2027")
print(f"instance {inst.name}: {len(inst.projects)} binary variables, gap target 0, one thread, seed 1")
for solver, api in (("HiGHS", "MathOpt"), ("SCIP", "MathOpt"), ("CP-SAT", "cp_model"), ("CBC", "pywraplp")):
    r = run(solver, inst, 1)
    work = ", ".join(f"{k} {v:g}" for k, v in r.work.items())
    print(f"  {solver:<7} via {api:<9} {r.status:<8} NPV {r.objective:,.0f}  bound {r.bound:,.0f}  "
          f"seed {'taken' if TAKES_SEED[solver] else 'not settable'}; reports {work}")

print("\nthe deterministic unit each reports, which the benchmark ranks it by:")
for solver, (unit, other) in MEASURES.items():
    print(f"  {solver:<7} {unit} (also {other})")

cbc, _ = build_wrapper(inst, "CBC")
print("\nCBC accepts solver-specific settings such as a seed:",
      cbc.SetSolverSpecificParametersAsString("randomSeed 2"))
