"""The GLOP and PDLP logs of the same funding LP (GridCap medium), times masked."""

from ortools.math_opt.python import mathopt

from funding_lp import build
from gridcap import generate
from solver_log import solve_with_log

lp = build(generate("medium"))
for solver in (mathopt.SolverType.GLOP, mathopt.SolverType.PDLP):
    result, log = solve_with_log(lp.model, solver)
    print(f"===== {solver.name}: {len(log)} log lines, {result.termination.reason.name}")
    for line in log:
        print(line)
