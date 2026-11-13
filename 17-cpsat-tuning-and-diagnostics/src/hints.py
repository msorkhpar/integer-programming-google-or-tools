"""Lesson 4.6.2: last cycle's plan as a solution hint on GridCap medium, with and without a budget cut.

GridCap is a fictional utility's portfolio. "Last cycle's plan" is the plan one worker finds in 3
units of deterministic time. Each re-plan gets 1 unit, with one worker, so every number repeats.
"""

from ortools.sat.python import cp_model

from cpsat_plan import build, schedule
from gridcap import generate

medium = generate("medium")


class FirstAndCount(cp_model.CpSolverSolutionCallback):
    def __init__(self) -> None:
        super().__init__()
        self.first = None
        self.count = 0

    def on_solution_callback(self) -> None:
        self.count += 1
        if self.first is None:
            self.first = self.objective_value


def one_worker(work: float | None = None) -> cp_model.CpSolver:
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1
    if work is not None:
        solver.parameters.max_deterministic_time = work
    return solver


def hint_plan(plan, starts: dict[str, int]) -> None:
    """Hint every start variable: 1 for the year the old plan starts the project, 0 otherwise."""
    for (pid, t), var in plan.x.items():
        plan.model.add_hint(var, 1 if starts.get(pid) == t else 0)


last = build(medium)
solver = one_worker(3.0)
solver.solve(last.model)
last_cycle = schedule(last, solver)
print(f"last cycle's plan: ${solver.objective_value:,.0f}k, {len(last_cycle)} projects")

for scale, scenario in ((1.0, "same budgets"), (0.97, "budgets cut 3%")):
    for hinted in (False, True):
        plan = build(medium, budget_scale=scale)
        if hinted:
            hint_plan(plan, last_cycle)
        solver, seen = one_worker(1.0), FirstAndCount()
        status = solver.solve(plan.model, seen)
        print(f"{scenario:<15} {'hint' if hinted else 'no hint':<8} {solver.status_name(status)}  "
              f"first ${seen.first:,.0f}k  best ${solver.objective_value:,.0f}k  plans {seen.count}")

for scale, scenario in ((1.0, "same budgets"), (0.97, "budgets cut 3%")):
    check = build(medium, budget_scale=scale)
    hint_plan(check, last_cycle)
    solver = one_worker()
    solver.parameters.fix_variables_to_their_hinted_value = True
    status = solver.solve(check.model)
    print(f"{scenario:<15} is last cycle's plan still feasible? {solver.status_name(status)}")
