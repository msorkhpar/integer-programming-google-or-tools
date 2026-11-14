"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from ortools.sat.python import cp_model

from vans import VanType, build

fleet = [VanType("cargo", 6, 400, 4, 2), VanType("truck", 15, 900, 2, 1), VanType("mini", 3, 150, 6, 3)]

for demand, budget, drivers in ((30, 3_000, 5), (45, 2_500, 4)):
    model, n = build(fleet, demand, budget, drivers)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 10
    status = solver.solve(model)
    label = f"demand {demand}, budget {budget}, drivers {drivers}:"
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        print(label, solver.status_name(status), {name: solver.value(v) for name, v in n.items()},
              "cost", round(solver.objective_value))
    else:
        print(label, solver.status_name(status))
