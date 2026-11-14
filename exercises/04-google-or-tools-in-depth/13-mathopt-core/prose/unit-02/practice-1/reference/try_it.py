"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

import datetime

from ortools.math_opt.python import mathopt

from verdict import verdict

S = mathopt.SolverType
params = mathopt.SolveParameters(time_limit=datetime.timedelta(seconds=10))

# Three night shifts under a 20-hour cap.
model = mathopt.Model(name="nights")
x = [model.add_binary_variable(name=f"n{i}") for i in range(3)]
model.add_linear_constraint(8 * x[0] + 9 * x[1] + 7 * x[2] <= 20, name="hours")
model.maximize(10 * x[0] + 12 * x[1] + 7 * x[2])
print("nights, cap 20:", verdict(mathopt.solve(model, S.HIGHS, params=params)))

model.add_linear_constraint(mathopt.fast_sum(x) >= 3, name="cover")
print("nights, cap 20, all three:", verdict(mathopt.solve(model, S.HIGHS, params=params)))

stopped = mathopt.SolveResult(termination=mathopt.Termination(
    reason=mathopt.TerminationReason.NO_SOLUTION_FOUND, limit=mathopt.Limit.TIME,
    objective_bounds=mathopt.ObjectiveBounds(primal_bound=float("-inf"), dual_bound=30.0)))
print("stopped by TIME with no plan:", verdict(stopped))
