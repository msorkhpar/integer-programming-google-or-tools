"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from ortools.math_opt.python import mathopt

from cash import Project, build

# A harbour board's capital works, $k.
works = [
    Project("E1", "East", (2031, 2032), (70,)),
    Project("E2", "East", (2032, 2033), (30, 30)),
    Project("W1", "West", (2031, 2032), (110,)),
    Project("W2", "West", (2033,), (80,)),
]
budgets = {2031: 80, 2032: 80, 2033: 80}


def allowed(plan, carry_share=0.5, floors=None):
    model, x = build(works, budgets, carry_share, floors or {})
    for (pid, t), var in x.items():
        var.lower_bound = var.upper_bound = 1.0 if plan.get(pid) == t else 0.0
    return mathopt.solve(model, mathopt.SolverType.HIGHS).termination.reason == mathopt.TerminationReason.OPTIMAL


print("W1 2032 alone, carry 50%:", allowed({"W1": 2032}))
print("W1 2032 alone, carry 25%:", allowed({"W1": 2032}, carry_share=0.25))
print("W1 2031 alone:", allowed({"W1": 2031}))
print("E1 2031, W2 2033, East floor 60:", allowed({"E1": 2031, "W2": 2033}, floors={"East": 60}))
print("W2 2033 alone, East floor 60:", allowed({"W2": 2033}, floors={"East": 60}))
