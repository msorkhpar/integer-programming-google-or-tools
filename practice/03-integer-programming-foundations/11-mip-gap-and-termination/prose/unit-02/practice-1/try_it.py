"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

import math

from ortools.math_opt.python import mathopt

from verdict import verdict

R, L = mathopt.TerminationReason, mathopt.Limit


def ended(reason, limit=None, primal=0.0, dual=0.0):
    return mathopt.Termination(reason=reason, limit=limit,
                               objective_bounds=mathopt.ObjectiveBounds(primal_bound=primal, dual_bound=dual))


print("OPTIMAL at 75:", verdict(ended(R.OPTIMAL, primal=75.0, dual=75.0)))
print("FEASIBLE, SOLUTION limit:", verdict(ended(R.FEASIBLE, L.SOLUTION, primal=70.0, dual=80.0)))
print("NO_SOLUTION_FOUND, TIME limit:", verdict(ended(R.NO_SOLUTION_FOUND, L.TIME, primal=-math.inf, dual=80.0)))
print("INFEASIBLE:", verdict(ended(R.INFEASIBLE, primal=-math.inf, dual=-math.inf)))
