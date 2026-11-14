"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from ortools.math_opt.python import mathopt

from upgrades import Limits, Project, build

# A ferry operator's pier upgrades.
piers = [
    Project("P1", 50, 2, "East", 14),
    Project("P2", 35, 3, "East", 11),
    Project("P3", 25, 2, "West", 7),
    Project("P4", 40, 4, "West", 13),
    Project("P5", 15, 1, "North", 5),
]
limits = Limits(budget=110, crew=8, region_cap={"East": 1, "West": 2, "North": 1},
                conflicts=[("P1", "P4")], needs=[("P5", "P3")])


def allowed(plan):
    model, x = build(piers, limits)
    for pid, var in x.items():
        var.lower_bound = var.upper_bound = 1.0 if pid in plan else 0.0
    return mathopt.solve(model, mathopt.SolverType.HIGHS).termination.reason == mathopt.TerminationReason.OPTIMAL


for plan in ({"P1", "P3", "P5"}, {"P1", "P2"}, {"P1", "P4"}, {"P5"}, {"P2", "P3", "P4"}):
    print(f"plan {sorted(plan)}:", allowed(plan))
model, x = build(piers, limits)
result = mathopt.solve(model, mathopt.SolverType.HIGHS)
print("best value:", round(result.objective_value()), sorted(p for p, v in x.items() if result.variable_values(v) > 0.5))
