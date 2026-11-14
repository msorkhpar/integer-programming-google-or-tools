"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from datetime import timedelta

from ortools.math_opt.python import mathopt

from crew_month import Job, build

# Sewer repairs with their crew hours: 80, 60, 30, 15, 45.
jobs = [Job("R1", 80), Job("R2", 60), Job("R3", 30), Job("R4", 15), Job("R5", 45)]
tiers = [(140, 50.0), (180, 80.0), (220, 110.0)]

def accepted(model):
    params = mathopt.SolveParameters(time_limit=timedelta(seconds=5))
    result = mathopt.solve(model, mathopt.SolverType.HIGHS, params=params)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def allowed(plan, budget):
    model, x = build(jobs, tiers, budget)
    for jid, var in x.items():
        var.lower_bound = var.upper_bound = 1.0 if jid in plan else 0.0
    return accepted(model)


print("R1 R2 (140 h) at budget 7000:", allowed({"R1", "R2"}, 7000))
print("R1 R2 R4 (155 h) at budget 8000:", allowed({"R1", "R2", "R4"}, 8000))
print("R1 R2 R4 (155 h) at budget 8300:", allowed({"R1", "R2", "R4"}, 8300))
print("R1 R2 R3 R5 (215 h) at budget 100000:", allowed({"R1", "R2", "R3", "R5"}, 100_000))
print("all jobs (230 h) at budget 100000:", allowed({"R1", "R2", "R3", "R4", "R5"}, 100_000))
