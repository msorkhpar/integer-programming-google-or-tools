"""Lesson 4.6.1: one worker against eight on GridCap medium, with the same deterministic budget per worker.

GridCap is a fictional utility's portfolio. One worker runs one search, so its numbers repeat run to
run and are printed. Eight workers race, so their exact numbers change from run to run (lesson
4.6.3); this program prints only what repeated in every run we made: the subsolvers the log lists
and whether the gap closed below 1%.
"""

from ortools.sat.python import cp_model

from cpsat_plan import build
from gridcap import generate

medium = generate("medium")


def gap(solver: cp_model.CpSolver) -> float:
    """Relative gap of a maximization: how far the proven bound is above the best plan found."""
    return (solver.best_objective_bound - solver.objective_value) / solver.objective_value


plan = build(medium)
solver = cp_model.CpSolver()
solver.parameters.num_workers = 1
solver.parameters.max_deterministic_time = 3.0
status = solver.solve(plan.model)
print(f"1 worker : {solver.status_name(status)}  plan ${solver.objective_value:,.0f}k  "
      f"bound ${solver.best_objective_bound:,.0f}k  gap {gap(solver):.2%}")

plan = build(medium)
solver = cp_model.CpSolver()
solver.parameters.num_workers = 8
solver.parameters.max_deterministic_time = 3.0
solver.parameters.log_search_progress = True
solver.parameters.log_to_stdout = False
log: list[str] = []
solver.log_callback = log.append
status = solver.solve(plan.model)
print(f"8 workers: {solver.status_name(status)}  gap below 1%: {gap(solver) < 0.01}")
for line in log:
    if "subsolver" in line and ": [" in line:
        print(" ", line)
