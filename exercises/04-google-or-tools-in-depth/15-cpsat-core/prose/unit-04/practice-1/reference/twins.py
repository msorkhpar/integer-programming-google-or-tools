from __future__ import annotations

from ortools.math_opt.python import mathopt
from ortools.sat.python import cp_model


def best_with_cpsat(value: dict[str, int], cost: dict[str, int], budget: int,
                    requires: list[tuple[str, str]], excludes: list[tuple[str, str]]) -> int:
    """The best total value, from CP-SAT with its own logic constraints."""
    model = cp_model.CpModel()
    x = {i: model.new_bool_var(i) for i in value}
    model.add(sum(cost[i] * x[i] for i in value) <= budget)
    for a, b in requires:
        model.add_implication(x[a], x[b])
    for a, b in excludes:
        model.add_bool_or(~x[a], ~x[b])
    model.maximize(sum(value[i] * x[i] for i in value))
    solver = cp_model.CpSolver()
    solver.solve(model)
    return round(solver.objective_value)


def best_with_highs(value: dict[str, int], cost: dict[str, int], budget: int,
                    requires: list[tuple[str, str]], excludes: list[tuple[str, str]]) -> int:
    """The best total value, from HiGHS through MathOpt with linear rows."""
    model = mathopt.Model()
    x = {i: model.add_binary_variable(name=i) for i in value}
    model.add_linear_constraint(sum(cost[i] * x[i] for i in value) <= budget)
    for a, b in requires:
        model.add_linear_constraint(x[a] <= x[b])
    for a, b in excludes:
        model.add_linear_constraint(x[a] + x[b] <= 1)
    model.maximize(sum(value[i] * x[i] for i in value))
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    return round(result.objective_value())


if __name__ == "__main__":
    value, cost = {"a": 5, "b": 4, "c": 3}, {"a": 4, "b": 3, "c": 2}
    print(best_with_cpsat(value, cost, 6, [("c", "b")], []), best_with_highs(value, cost, 6, [("c", "b")], []))
