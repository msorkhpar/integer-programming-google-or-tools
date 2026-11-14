"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from ortools.sat.python import cp_model

from repeatable import repeatable_solver

# Eight hedge-cutting jobs, (value, hours), and 30 hours of crew time.
jobs = [(40, 9), (25, 6), (33, 8), (18, 4), (29, 7), (12, 3), (36, 10), (21, 5)]


def solve(seed, work):
    model = cp_model.CpModel()
    pick = [model.new_bool_var(f"job{i}") for i in range(len(jobs))]
    model.add(sum(h * p for (_, h), p in zip(jobs, pick)) <= 30)
    model.maximize(sum(v * p for (v, _), p in zip(jobs, pick)))
    solver = repeatable_solver(seed, work)
    status = solver.solve(model)
    return solver, (solver.status_name(status), solver.objective_value, solver.num_branches, solver.num_conflicts)


solver, first = solve(9, 1.0)
_, second = solve(9, 1.0)
print("workers, seed, work limit:", solver.parameters.num_workers, solver.parameters.random_seed,
      solver.parameters.max_deterministic_time)
print("seed 9, first run (status, objective, branches, conflicts):", first)
print("seed 9, second run:", second)
