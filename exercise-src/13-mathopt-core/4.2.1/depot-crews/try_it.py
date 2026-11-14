"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

import datetime

from ortools.math_opt.python import mathopt

from crews import Depot, build

depots = [Depot("Quay", 4, 3.5, 6.0), Depot("Weir", 3, 2.0, 11.0), Depot("Moor", 2, 4.0, 1.0)]
params = mathopt.SolveParameters(time_limit=datetime.timedelta(seconds=10))

for low, high in ((3, 5), (6, 8)):
    model, open_, crews = build(depots, low, high)
    result = mathopt.solve(model, mathopt.SolverType.HIGHS, params=params)
    print(f"band {low}..{high}:", result.termination.reason.name)
    if result.has_primal_feasible_solution():
        print(f"  cost at band {low}..{high}:", round(result.objective_value(), 2))
        print(f"  crews at band {low}..{high}:", {n: round(result.variable_values(v)) for n, v in crews.items()})
