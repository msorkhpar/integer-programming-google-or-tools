"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from ortools.sat.python import cp_model

from crew import Job, build

jobs = [Job("Pump", 2, 0, 8), Job("Valve", 3, 1, 12), Job("Tank", 1, 4, 15)]
blocked = [(3, 4)]


def allowed(starts):
    model, start = build(jobs, blocked, 16)
    for name, week in starts.items():
        model.add(start[name] == week)
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1
    solver.parameters.max_time_in_seconds = 5
    return solver.solve(model) in (cp_model.OPTIMAL, cp_model.FEASIBLE)


print("Pump 0, Valve 5, Tank 8:", allowed({"Pump": 0, "Valve": 5, "Tank": 8}))
print("Pump 0, Valve 1, Tank 8:", allowed({"Pump": 0, "Valve": 1, "Tank": 8}))
print("Pump 2, Valve 5, Tank 8:", allowed({"Pump": 2, "Valve": 5, "Tank": 8}))
print("Pump 6, Valve 9, Tank 12:", allowed({"Pump": 6, "Valve": 9, "Tank": 12}))
model, start = build(jobs, blocked, 16)
solver = cp_model.CpSolver()
solver.parameters.num_workers = 1
solver.parameters.max_time_in_seconds = 5
status = solver.solve(model)
print("free schedule:", solver.status_name(status), {n: solver.value(v) for n, v in start.items()})
