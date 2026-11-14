"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from ortools.sat.python import cp_model

from roster_solver import configure

# Two crews, four parks; each park mown by one crew; a crew mows at most two.
model = cp_model.CpModel()
x = {(p, c): model.new_bool_var(f"x_{p}_{c}") for p in range(4) for c in range(2)}
for p in range(4):
    model.add_exactly_one(x[p, c] for c in range(2))
for c in range(2):
    model.add(sum(x[p, c] for p in range(4)) <= 2)
model.maximize(sum((p + 2) * (c + 1) % 4 * x[p, c] for p in range(4) for c in range(2)))

solver = configure(cp_model.CpSolver(), seed=23, workers=2, work=3.0)
print("seed:", solver.parameters.random_seed)
print("workers:", solver.parameters.num_workers)
print("work limit:", solver.parameters.max_deterministic_time)
print("interleave search:", solver.parameters.interleave_search)
status = solver.solve(model)
print("status:", solver.status_name(status), "objective:", solver.objective_value)
