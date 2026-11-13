from __future__ import annotations

from ortools.math_opt.python import mathopt


def build_named(poles: int, cost: dict, risk: dict, crew: dict, *, integer: bool = True):
    """One binary per pole and year: the model a first draft writes. x[p, y] = 1: pole p replaced in y."""
    years = sorted(cost)
    model = mathopt.Model(name="poles, named")
    x = {(p, y): model.add_variable(lb=0, ub=1, is_integer=integer, name=f"x_{p}_{y}")
         for p in range(poles) for y in years}
    for p in range(poles):
        model.add_linear_constraint(sum(x[p, y] for y in years) == 1, name=f"replaced_{p}")
    for y in years:
        model.add_linear_constraint(sum(x[p, y] for p in range(poles)) <= crew[y], name=f"crew_{y}")
    waiting = {y: poles - sum(x[p, u] for p in range(poles) for u in years if u <= y) for y in years}
    model.minimize(sum(cost[y] * x[p, y] for p in range(poles) for y in years)
                   + sum(risk[y] * waiting[y] for y in years))
    return model, x


def build_counted(poles: int, cost: dict, risk: dict, crew: dict, *, integer: bool = True):
    """The same plan with the identical poles counted: n[y] poles are replaced in year y."""
    # TODO: variables, rows and objective of the counted model.
    return mathopt.Model(name="poles, counted"), {}


if __name__ == "__main__":
    cost = {2027: 9, 2028: 10, 2029: 11, 2030: 12}
    risk = {2027: 3, 2028: 3, 2029: 4, 2030: 0}
    crew = {2027: 8, 2028: 10, 2029: 10, 2030: 12}
    for build in (build_named, build_counted):
        model, v = build(30, cost, risk, crew)
        print(build.__name__, len(v), "variables", mathopt.solve(model, mathopt.SolverType.HIGHS).objective_value())
