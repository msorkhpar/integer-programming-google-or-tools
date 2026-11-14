"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from ortools.math_opt.python import mathopt

from outages import Project, build

feeders = [Project("K1", (2030, 2031), must_do=True), Project("K2", (2030, 2031)),
           Project("K3", (2031, 2032)), Project("K4", (2030,)), Project("K5", (2032,))]
crews = {2030: 2, 2031: 1, 2032: 1}
shared = [("K2", "K3")]


def allowed(schedule):
    model, x = build(feeders, crews, shared)
    for (pid, t), var in x.items():
        var.lower_bound = var.upper_bound = 1.0 if t in schedule.get(pid, []) else 0.0
    return mathopt.solve(model, mathopt.SolverType.HIGHS).termination.reason == mathopt.TerminationReason.OPTIMAL


print("K1 2030, K4 2030, K5 2032:", allowed({"K1": [2030], "K4": [2030], "K5": [2032]}))
print("K1 2030, K4 2030, K2 2030:", allowed({"K1": [2030], "K4": [2030], "K2": [2030]}))
print("K1 2030, K2 2031, K3 2031:", allowed({"K1": [2030], "K2": [2031], "K3": [2031]}))
print("K1 2030, K2 2030, K3 2031:", allowed({"K1": [2030], "K2": [2030], "K3": [2031]}))
print("K1 2031, K2 2031, K3 2031:", allowed({"K1": [2031], "K2": [2031], "K3": [2031]}))
