"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from ortools.math_opt.python import mathopt

from rules import add_share_rules

AREAS = ("parks", "roads", "libraries")


def allowed(plan, max_share, pairs):
    """Fix every amount to the plan's value and ask GLOP whether the rows allow it."""
    model = mathopt.Model()
    spend = {k: model.add_variable(lb=plan[k], ub=plan[k], name=k) for k in AREAS}
    add_share_rules(model, spend, max_share, pairs)
    result = mathopt.solve(model, mathopt.SolverType.GLOP)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


print("plan 30/40/30, share 0.4:", allowed({"parks": 30, "roads": 40, "libraries": 30}, 0.4, []))
print("plan 20/55/25, share 0.4:", allowed({"parks": 20, "roads": 55, "libraries": 25}, 0.4, []))
pairs = [("parks", "libraries", 1.5)]
print("plan 30/40/30, share 0.4, parks >= 1.5 libraries:", allowed({"parks": 30, "roads": 40, "libraries": 30}, 0.4, pairs))
