"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

import random

from ortools.sat.python import cp_model

from stopper import TargetStopper

# Twenty crates for a van with 80 units of room.
rng = random.Random(11)
values = [rng.randint(4, 30) for _ in range(20)]
weights = [rng.randint(2, 15) for _ in range(20)]
model = cp_model.CpModel()
x = [model.new_bool_var(f"crate{i}") for i in range(20)]
model.add(sum(w * v for w, v in zip(weights, x)) <= 80)
model.maximize(sum(c * v for c, v in zip(values, x)))

for target in (150, 10_000):
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1
    solver.parameters.max_time_in_seconds = 10
    solver.parameters.cp_model_presolve = False
    solver.parameters.linearization_level = 0
    stopper = TargetStopper(target)
    status = solver.solve(model, stopper)
    print(f"target {target}:", solver.status_name(status), "values seen", stopper.objectives)
