from __future__ import annotations

from ortools.sat.python import cp_model


def repeatable_solver(seed: int, work: float) -> cp_model.CpSolver:
    """A CP-SAT solver whose every count repeats run to run: one worker, a seed, a work limit."""
    solver = cp_model.CpSolver()
    # TODO: the settings that make every run repeat.
    return solver


if __name__ == "__main__":
    model = cp_model.CpModel()
    x = [model.new_bool_var(f"x{i}") for i in range(6)]
    model.add(sum((i + 2) * v for i, v in enumerate(x)) <= 10)
    model.maximize(sum((i + 3) * v for i, v in enumerate(x)))
    solver = repeatable_solver(7, 1.0)
    print(solver.status_name(solver.solve(model)), solver.objective_value)
