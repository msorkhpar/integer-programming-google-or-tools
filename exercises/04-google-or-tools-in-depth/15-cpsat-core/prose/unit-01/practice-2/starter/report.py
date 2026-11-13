from __future__ import annotations

from ortools.sat.python import cp_model


def report(model: cp_model.CpModel, x: dict, solver: cp_model.CpSolver | None = None) -> dict:
    """Solve and say what came back: status, plan, objective, whether it is proven best, and why not valid."""
    # TODO: solve, then fill in what the status allows you to read.
    return {"status": "", "plan": None, "objective": None, "proven": False, "reason": ""}

if __name__ == "__main__":
    model = cp_model.CpModel()
    x = {name: model.new_bool_var(name) for name in ("a", "b", "c")}
    model.add(2 * x["a"] + 3 * x["b"] + 4 * x["c"] <= 5)
    model.maximize(3 * x["a"] + 4 * x["b"] + 5 * x["c"])
    print(report(model, x))
