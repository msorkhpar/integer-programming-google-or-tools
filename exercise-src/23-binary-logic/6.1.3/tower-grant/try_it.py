"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from datetime import timedelta

from ortools.math_opt.python import mathopt

from grant import Tower, build

# Towers in two counties, with hub H1 needing one backhaul link.
towers = [Tower(f"H{k}", "Hill") for k in range(1, 4)] + [Tower(f"V{k}", "Vale") for k in range(1, 4)]
need = {"Hill": 2, "Vale": 2}
already = {"Vale": 1}
crew_limit = {"Hill": 2}
backhaul = {"H1": ["H1-fiber", "H1-radio"]}
plan = {"H1", "H1-radio", "H2", "V1"}


def allowed(chosen):
    model, x, y = build(towers, need, already, crew_limit, backhaul)
    for key, var in {**x, **y}.items():
        var.lower_bound = var.upper_bound = 1.0 if key in chosen else 0.0
    params = mathopt.SolveParameters(time_limit=timedelta(seconds=5))
    result = mathopt.solve(model, mathopt.SolverType.HIGHS, params=params)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


print("H1 H1-radio H2 V1:", allowed(plan))
print("without V1:", allowed(plan - {"V1"}))
print("plus H3:", allowed(plan | {"H3"}))
print("without H1-radio:", allowed(plan - {"H1-radio"}))
print("plus H1-fiber:", allowed(plan | {"H1-fiber"}))
