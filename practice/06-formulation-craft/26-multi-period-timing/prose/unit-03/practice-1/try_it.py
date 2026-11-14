"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from datetime import timedelta

from ortools.math_opt.python import mathopt

from deadline import Project, add_deadline_rows, start_variables

def solve_ok(model):
    params = mathopt.SolveParameters(time_limit=timedelta(seconds=5))
    result = mathopt.solve(model, mathopt.SolverType.HIGHS, params=params)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def allowed(schedule, within):
    first, second = Project("BY", (2031, 2032)), Project("RP", (2031, 2032, 2033, 2034))
    model = mathopt.Model()
    x = start_variables(model, [first, second])
    for p in (first, second):
        model.add_linear_constraint(sum(x[p.pid, t] for t in p.starts) <= 1)
    add_deadline_rows(model, x, first, second, within)
    for (pid, t), var in x.items():
        var.lower_bound = var.upper_bound = 1.0 if schedule.get(pid) == t else 0.0
    return solve_ok(model)


print("BY 2031, RP 2033, within 2:", allowed({"BY": 2031, "RP": 2033}, 2))
print("BY 2031, RP 2034, within 2:", allowed({"BY": 2031, "RP": 2034}, 2))
print("BY 2032, RP 2031, within 3:", allowed({"BY": 2032, "RP": 2031}, 3))
print("RP 2032 alone, within 3:", allowed({"RP": 2032}, 3))
print("nothing, within 1:", allowed({}, 1))
