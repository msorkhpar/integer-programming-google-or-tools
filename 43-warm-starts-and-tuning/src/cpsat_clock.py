"""Which of CP-SAT's counters can date an incumbent? Read them in a solution callback, with one worker."""

from ortools.sat.python import cp_model

from plan_model import build_cpsat, instance_set


class Clocks(cp_model.CpSolverSolutionCallback):
    """At each new plan: deterministic time, branches and conflicts so far, and the plan's NPV."""

    def __init__(self) -> None:
        super().__init__()
        self.seen: list[tuple[float, int, int, float]] = []

    def on_solution_callback(self) -> None:
        self.seen.append((round(self.deterministic_time, 4), self.num_branches, self.num_conflicts,
                          self.objective_value))


ridge = instance_set()[0]
model, _ = build_cpsat(ridge)
solver = cp_model.CpSolver()
solver.parameters.num_workers = 1                       # lesson 4.6.3: one worker repeats exactly
solver.parameters.random_seed = 1
clocks = Clocks()
solver.solve(model, clocks)
first, last = clocks.seen[0], clocks.seen[-1]
print(f"1 worker: {len(clocks.seen)} plans; at the end of the solve "
      f"deterministic time {solver.deterministic_time:.4f}, branches {solver.num_branches:,}")
print(f"  first plan: det. time {first[0]:.4f}, branches {first[1]:>7,}, NPV {first[3]:,.0f}")
print(f"  last plan:  det. time {last[0]:.4f}, branches {last[1]:>7,}, NPV {last[3]:,.0f}")
