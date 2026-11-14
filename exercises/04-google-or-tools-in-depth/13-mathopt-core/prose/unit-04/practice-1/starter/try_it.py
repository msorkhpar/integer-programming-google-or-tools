"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from ortools.math_opt.python import mathopt

from params import params_for

S = mathopt.SolverType


def show(p):
    return (f"time {p.time_limit}, gap {p.relative_gap_tolerance}, threads {p.threads}, "
            f"seed {p.random_seed}, solutions {p.solution_limit}")


for solver in (S.GLOP, S.PDLP, S.HIGHS, S.GSCIP, S.CP_SAT):
    print(f"{solver.name}, 20 s, gap 0.03, 2 threads, seed 5:", show(params_for(solver, 20, 0.03, 2, 5)))
print("HIGHS, first plan:", show(params_for(S.HIGHS, 20, 0.03, 2, 5, first_plan=True)))
