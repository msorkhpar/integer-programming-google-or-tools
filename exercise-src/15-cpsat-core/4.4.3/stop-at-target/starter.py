from __future__ import annotations

from ortools.sat.python import cp_model


class TargetStopper(cp_model.CpSolverSolutionCallback):
    """Record each solution's objective, and stop the search at the first one that reaches the target."""

    def __init__(self, target: float):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.target = target
        self.objectives: list[float] = []

    def on_solution_callback(self) -> None:
        # TODO: record the objective, and stop once the target is reached.
        return None

if __name__ == "__main__":
    model = cp_model.CpModel()
    x = [model.new_bool_var(f"x{i}") for i in range(4)]
    model.add(3 * x[0] + 4 * x[1] + 5 * x[2] + 6 * x[3] <= 10)
    model.maximize(4 * x[0] + 5 * x[1] + 6 * x[2] + 8 * x[3])
    stopper = TargetStopper(10)
    solver = cp_model.CpSolver()
    print(solver.status_name(solver.solve(model, stopper)), stopper.objectives)
