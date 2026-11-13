from __future__ import annotations

from ortools.sat.python import cp_model


def record(solver: cp_model.CpSolver, status, pick: dict[str, cp_model.IntVar]) -> tuple:
    """What a repeatable run is compared on: status name, objective, and the chosen names in order."""
    # TODO: status name, objective, chosen names.
    return ()


if __name__ == "__main__":
    model = cp_model.CpModel()
    pick = {name: model.new_bool_var(name) for name in ("b", "a")}
    model.add(sum(pick.values()) <= 1)
    model.maximize(2 * pick["a"] + pick["b"])
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1
    print(record(solver, solver.solve(model), pick))
