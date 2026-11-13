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
    # TODO: write the step's model first: which variables are fixed, and to what.
    return {}


if __name__ == "__main__":
    projects = {"main line": {"value": {2027: 10, 2028: 12}, "cost": [10]}, "valves": {"value": {2027: 8}, "cost": [10]}}
    print(lns_step(projects, {2027: 10, 2028: 10}, {"valves": 2027}, {"main line"}))
