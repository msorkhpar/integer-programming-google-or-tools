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
    model.maximize(objective)
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1
    if solver.solve(model) != cp_model.OPTIMAL:
        return None, []
    best = round(solver.objective_value)

    model.add(objective == best)
    model.clear_objective()
    collector = PlanCollector(x)
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1
    solver.parameters.enumerate_all_solutions = True
    solver.solve(model, collector)
    return best, sorted(set(collector.plans))


if __name__ == "__main__":
    model = cp_model.CpModel()
    x = {t: model.new_bool_var(t) for t in ("A", "B", "C")}
    model.add(sum(x.values()) <= 2)
    print(all_best(model, x, x["A"] + x["B"] + x["C"]))
