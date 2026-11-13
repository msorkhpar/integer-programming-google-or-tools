from __future__ import annotations

from ortools.math_opt.python import mathopt


def add_commissioning(model: mathopt.Model, x: dict, z: dict, jobs_of: dict) -> None:
    """A substation is commissioned (z = 1) only if every one of its jobs is funded."""
    for s, jobs in jobs_of.items():
        for j in jobs:
            model.add_linear_constraint(z[s] <= x[j], name=f"needs_{s}_{j}")


def build(cost: dict, value: dict, budget: int, bonus: dict, jobs_of: dict,
          *, integer: bool = True) -> tuple[mathopt.Model, dict, dict]:
    """Fund jobs within the budget; a commissioned substation earns its bonus."""
    model = mathopt.Model(name="commissioning")
    x = {j: model.add_variable(lb=0, ub=1, is_integer=integer, name=f"x_{j}") for j in cost}
    z = {s: model.add_variable(lb=0, ub=1, is_integer=integer, name=f"z_{s}") for s in jobs_of}
    model.add_linear_constraint(sum(cost[j] * x[j] for j in cost) <= budget, name="budget")
    add_commissioning(model, x, z, jobs_of)
    model.maximize(sum(value[j] * x[j] for j in cost) + sum(bonus[s] * z[s] for s in jobs_of))
    return model, x, z


def add_colleague_rows(model: mathopt.Model, x: dict, z: dict, jobs_of: dict) -> None:
    """The colleague's version: one row per substation, |J_s| z_s <= sum of its jobs."""
    for s, jobs in jobs_of.items():
        model.add_linear_constraint(len(jobs) * z[s] <= sum(x[j] for j in jobs), name=f"needs_{s}")


if __name__ == "__main__":
    cost = {"T1": 4, "T2": 3, "B1": 2}
    model, x, z = build(cost, {"T1": 1, "T2": 1, "B1": 1}, 7, {"North": 6}, {"North": ["T1", "T2", "B1"]},
                        integer=False)
    print(mathopt.solve(model, mathopt.SolverType.GLOP).objective_value())
