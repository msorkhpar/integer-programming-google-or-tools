"""Lesson 4.4.3: a solution callback that sees every improving plan, and one that stops the search.

The printer is adapted from the OR-Tools example solve_and_print_intermediate_solutions_sample_sat.py,
https://github.com/google/or-tools/blob/stable/ortools/sat/samples (Apache-2.0). GridCap is a
fictional utility's portfolio; the model is lesson 4.4.1's selection on GridCap medium.
"""

from ortools.sat.python import cp_model

from gridcap import generate
from cpsat_models import one_worker, selection


class ObjectivePrinter(cp_model.CpSolverSolutionCallback):
    """Record the objective and bound of each solution the search finds."""

    def __init__(self, x: dict):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.x = x
        self.seen = []

    def on_solution_callback(self) -> None:
        count = sum(self.boolean_value(v) for v in self.x.values())
        self.seen.append((self.objective_value, self.best_objective_bound, count))


class StopWithinGap(cp_model.CpSolverSolutionCallback):
    """Stop the search at the first solution within `gap` of the bound (relative)."""

    def __init__(self, gap: float):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.gap = gap
        self.solution_count = 0

    def on_solution_callback(self) -> None:
        self.solution_count += 1
        if self.best_objective_bound - self.objective_value <= self.gap * abs(self.objective_value):
            self.stop_search()


medium = generate("medium")
sel = selection(medium, native=True)

runs = []
for run in range(2):
    printer = ObjectivePrinter(sel.x)
    solver = one_worker()
    status = solver.solve(sel.model, printer)
    runs.append(printer.seen)
print(f"{solver.status_name(status)}: {len(printer.seen)} improving solutions; the first five and the last:")
for objective, bound, count in printer.seen[:5] + printer.seen[-1:]:
    print(f"  objective {objective:>9,.0f}  bound {bound:>9,.0f}  projects {count}")
print("second run, same sequence:", runs[0] == runs[1])

stopper = StopWithinGap(0.005)
solver = one_worker()
status = solver.solve(sel.model, stopper)
print(f"stopped within 0.5%: {solver.status_name(status)} after {stopper.solution_count} solutions,"
      f" objective {solver.objective_value:,.0f}, bound {solver.best_objective_bound:,.0f}")
