"""The end of the log: HiGHS's violation lines and SCIP's warning, on a sound run and a leaky one."""

from ortools.math_opt.python import mathopt

from gridcap import generate
from loan_model import EXACT, HUGE_M, NO_PRESOLVE, TIGHT, build, solve

small = generate("small")
for label, units, params in (("tight M, defaults", TIGHT, EXACT), ("M = 1e9, presolve off", HUGE_M, NO_PRESOLVE)):
    _, log = solve(build(small, units).model, params=params)
    start = next(i for i, line in enumerate(log) if "Solution status" in line)
    print(f"HiGHS, {label}:")
    for line in log[start:start + 5]:
        print(line)

result, log = solve(build(small, HUGE_M).model, mathopt.SolverType.GSCIP, EXACT)
print(f"SCIP, M = 1e9, defaults: {result.termination.reason.name}, objective {result.objective_value():,.1f}")
start = next(i for i, line in enumerate(log) if line.startswith("SCIP Status"))
for line in log[start:]:
    print(line)
