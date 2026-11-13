from __future__ import annotations

from ortools.sat.python import cp_model


def report(model: cp_model.CpModel, x: dict, solver: cp_model.CpSolver | None = None) -> dict:
    """Solve and say what came back: status, plan, objective, whether it is proven best, and why not valid."""
    solver = solver or cp_model.CpSolver()
    status = solver.solve(model)
    answer = {"status": solver.status_name(status), "plan": None, "objective": None, "proven": False, "reason": ""}
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        answer["plan"] = sorted(name for name, var in x.items() if solver.boolean_value(var))
        if model.has_objective():
            answer["objective"] = round(solver.objective_value)
        answer["proven"] = status == cp_model.OPTIMAL
    elif status == cp_model.MODEL_INVALID:
        answer["reason"] = model.validate()
    return answer


if __name__ == "__main__":
    model = cp_model.CpModel()
    x = {name: model.new_bool_var(name) for name in ("a", "b", "c")}
    model.add(2 * x["a"] + 3 * x["b"] + 4 * x["c"] <= 5)
    model.maximize(3 * x["a"] + 4 * x["b"] + 5 * x["c"])
    print(report(model, x))
