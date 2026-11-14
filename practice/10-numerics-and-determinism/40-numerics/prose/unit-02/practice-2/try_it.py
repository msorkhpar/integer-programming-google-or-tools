"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from datetime import timedelta

from ortools.math_opt.python import mathopt

from fleet import build_scaled

fleet = build_scaled()
sizes = [abs(row.get_coefficient(v)) for row in fleet.model.linear_constraints() for v in fleet.model.row_nonzeros(row)]
print("matrix span of the $k model:", round(max(sizes) / min(sizes), 1))

result = mathopt.solve(fleet.model, mathopt.SolverType.HIGHS, params=mathopt.SolveParameters(time_limit=timedelta(seconds=5)))
print("status:", result.termination.reason.name)
print("best value, $k:", round(result.objective_value(), 1))
print("orders bought:", sorted(n for n, v in fleet.buy.items() if result.variable_values(v) > 0.5))
print("overdraft, $k:", round(result.variable_values(fleet.overdraft), 1))
