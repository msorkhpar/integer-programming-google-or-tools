"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

import datetime

from ortools.math_opt.python import mathopt

from units import Unit, build

units = [Unit("G1", 12, 30), Unit("G2", 20, 50), Unit("G3", 8, 15)]
params = mathopt.SolveParameters(time_limit=datetime.timedelta(seconds=10))

for demand in (14, 45, 85):
    model, on, power = build(units, demand)
    result = mathopt.solve(model, mathopt.SolverType.GSCIP, params=params)
    print(f"demand {demand}:", result.termination.reason.name, "indicators", model.get_num_indicator_constraints())
    if result.has_primal_feasible_solution():
        print(f"  output at demand {demand}:", {n: round(result.variable_values(v), 2) for n, v in power.items()})
