from __future__ import annotations

import math

from ortools.math_opt.python import mathopt


def solve_dual(value: dict[str, float],
               rows: dict[str, tuple[dict[str, float], str, float]]) -> tuple[float | None, dict[str, float]]:
    """Build and solve the dual of the maximization LP; return its optimal value and the row prices."""
    dual = mathopt.Model(name="dual")
    price = {}
    for name, (_, sense, _) in rows.items():
        if sense == "<=":
            price[name] = dual.add_variable(lb=0, name=f"y_{name}")
        elif sense == ">=":
            price[name] = dual.add_variable(lb=-math.inf, ub=0, name=f"y_{name}")
        else:
            price[name] = dual.add_variable(lb=-math.inf, ub=math.inf, name=f"y_{name}")
    for activity, worth in value.items():
        column = sum(coeffs.get(activity, 0) * price[name] for name, (coeffs, _, _) in rows.items())
        dual.add_linear_constraint(column >= worth, name=f"cover_{activity}")
    dual.minimize(sum(rhs * price[name] for name, (_, _, rhs) in rows.items()))
    result = mathopt.solve(dual, mathopt.SolverType.GLOP)
    if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
        return None, {}
    return result.objective_value(), {name: result.variable_values(y) for name, y in price.items()}


if __name__ == "__main__":
    value = {"inspect": 4, "repair": 3}
    rows = {"hours": ({"inspect": 1, "repair": 1}, "<=", 10), "inspect_cap": ({"inspect": 1}, "<=", 6)}
    print(solve_dual(value, rows))
