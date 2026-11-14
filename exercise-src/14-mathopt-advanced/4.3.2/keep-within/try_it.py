"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from ortools.math_opt.python import mathopt

from keep import keep_within


def accepts(value, best, is_maximize, params):
    model = mathopt.Model()
    margin = model.add_variable(lb=-1e6, ub=1e6, name="margin")
    keep_within(model, 3 * margin, best, is_maximize, params)
    margin.lower_bound = margin.upper_bound = value / 3
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


REL2 = mathopt.ObjectiveParameters(objective_degradation_relative_tolerance=0.02)
ABS9 = mathopt.ObjectiveParameters(objective_degradation_absolute_tolerance=9)
print("max, best 600, 2 percent, value 588:", accepts(588, 600, True, REL2))
print("max, best 600, 2 percent, value 585:", accepts(585, 600, True, REL2))
print("min, best 300, absolute 9, value 309:", accepts(309, 300, False, ABS9))
print("min, best 300, no tolerance, value 301:", accepts(301, 300, False, None))
