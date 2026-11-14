"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from ortools.math_opt.python import mathopt

from guard import next_step

R = mathopt.TerminationReason


def ended(reason, limit=None, primal=0.0, dual=0.0):
    bounds = mathopt.ObjectiveBounds(primal_bound=primal, dual_bound=dual)
    return mathopt.SolveResult(termination=mathopt.Termination(reason=reason, limit=limit, objective_bounds=bounds))


print("optimal at 310:", next_step(ended(R.OPTIMAL, primal=310.0, dual=310.0), 0.02))
print("feasible 300 vs bound 303, max gap 2%:", next_step(ended(R.FEASIBLE, mathopt.Limit.TIME, 300.0, 303.0), 0.02))
print("feasible 300 vs bound 330, max gap 2%:", next_step(ended(R.FEASIBLE, mathopt.Limit.TIME, 300.0, 330.0), 0.02))
print("infeasible:", next_step(ended(R.INFEASIBLE), 0.02))
print("infeasible or unbounded:", next_step(ended(R.INFEASIBLE_OR_UNBOUNDED), 0.02))
print("no solution, node limit:", next_step(ended(R.NO_SOLUTION_FOUND, mathopt.Limit.NODE), 0.02))
