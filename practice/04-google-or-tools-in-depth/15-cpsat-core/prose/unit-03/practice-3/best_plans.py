from __future__ import annotations

from ortools.sat.python import cp_model


class PlanCollector(cp_model.CpSolverSolutionCallback):
    """Keep the names whose Boolean is true, for every solution reported."""

    def __init__(self, x: dict):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.x = x
        self.plans: list[tuple[str, ...]] = []

    def on_solution_callback(self) -> None:
        self.plans.append(tuple(sorted(name for name, v in self.x.items() if self.boolean_value(v))))


def all_best(model: cp_model.CpModel, x: dict, objective) -> tuple[int | None, list[tuple[str, ...]]]:
    """The best value of `objective` (maximized) and every distinct plan that reaches it, sorted."""
    # TODO: find the best value, then every plan that reaches it.
    return None, []

if __name__ == "__main__":
    model = cp_model.CpModel()
    x = {t: model.new_bool_var(t) for t in ("A", "B", "C")}
    model.add(sum(x.values()) <= 2)
    print(all_best(model, x, x["A"] + x["B"] + x["C"]))
