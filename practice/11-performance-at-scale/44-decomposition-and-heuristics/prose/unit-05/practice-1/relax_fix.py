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


def relax_and_fix(projects: dict, budgets: dict[int, float], window: int, keep: int) -> dict[str, int]:
    """Plan `window` years as integers with every later year relaxed; keep the first `keep` years; roll on."""
    # TODO: write one window's model first, then the loop.
    return {}


if __name__ == "__main__":
    projects = {"main line": {"value": {2027: 10}, "cost": [10, 10]}, "valves": {"value": {2027: 8}, "cost": [10]}}
    print(relax_and_fix(projects, {2027: 10, 2028: 10}, 1, 1))
