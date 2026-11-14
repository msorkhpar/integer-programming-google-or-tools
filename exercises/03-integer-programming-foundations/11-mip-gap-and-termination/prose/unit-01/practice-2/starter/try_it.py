"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

import math

from ortools.math_opt.python import mathopt

from gap import read_gap


def ended(primal, dual, reason=mathopt.TerminationReason.FEASIBLE, limit=mathopt.Limit.TIME):
    return mathopt.SolveResult(termination=mathopt.Termination(
        reason=reason, limit=limit, objective_bounds=mathopt.ObjectiveBounds(primal_bound=primal, dual_bound=dual)))


print("primal 2400, dual 2460:", read_gap(ended(2_400.0, 2_460.0)))
print("primal 310, dual 300:", read_gap(ended(310.0, 300.0)))
print("primal 0, dual 15:", read_gap(ended(0.0, 15.0)))
print("no plan, dual 2460:", read_gap(ended(-math.inf, 2_460.0, mathopt.TerminationReason.NO_SOLUTION_FOUND)))
