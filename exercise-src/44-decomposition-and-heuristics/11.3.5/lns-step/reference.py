from __future__ import annotations

from ortools.math_opt.python import mathopt


def build(projects: dict, budgets: dict[int, float]):
    """The whole plan: at most one start per project, spend within every year's budget."""
    model = mathopt.Model(name="fleet plan")
    x = {(n, t): model.add_binary_variable(name=f"x_{n}_{t}") for n, p in projects.items() for t in p["value"]}
    for n, p in projects.items():
        model.add_linear_constraint(sum(x[n, t] for t in p["value"]) <= 1, name=f"once_{n}")
    for y, b in budgets.items():
        spend = mathopt.LinearExpression()
        for (n, t), var in x.items():
            for k, c in enumerate(projects[n]["cost"]):
                if t + k == y:
                    spend += c * var
        model.add_linear_constraint(spend <= b, name=f"budget_{y}")
    model.maximize(sum(projects[n]["value"][t] * var for (n, t), var in x.items()))
    return model, x


def lns_step(projects: dict, budgets: dict[int, float], plan: dict[str, int], free: set[str]) -> dict[str, int]:
    """Re-plan the projects in `free`, keep every other project as `plan` has it; never return worse."""
    model, x = build(projects, budgets)
    for (n, t), var in x.items():
        if n not in free:
            var.lower_bound = var.upper_bound = 1 if plan.get(n) == t else 0
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    found = {n: t for (n, t), var in x.items() if result.variable_values(var) > 0.5}
    worth = lambda p: sum(projects[n]["value"][t] for n, t in p.items())
    return found if worth(found) > worth(plan) else dict(plan)


if __name__ == "__main__":
    projects = {"main line": {"value": {2027: 10, 2028: 12}, "cost": [10]}, "valves": {"value": {2027: 8}, "cost": [10]}}
    print(lns_step(projects, {2027: 10, 2028: 10}, {"valves": 2027}, {"main line"}))
