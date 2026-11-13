from __future__ import annotations

from ortools.math_opt.python import mathopt


def total_violation(rows: list[tuple[list[float], str, float]]) -> float:
    """The least total stretch v_r >= 0 that lets some x >= 0 satisfy every row."""
    n = len(rows[0][0])
    model = mathopt.Model(name="phase-one")
    x = [model.add_variable(lb=0, name=f"x{j}") for j in range(n)]
    v = [model.add_variable(lb=0, name=f"v{i}") for i in range(len(rows))]
    for i, (a, sense, b) in enumerate(rows):
        lhs = sum(a[j] * x[j] for j in range(n))
        if sense == "<=":
            model.add_linear_constraint(lhs - v[i] <= b, name=f"row{i}")
        else:
            model.add_linear_constraint(lhs + v[i] >= b, name=f"row{i}")
    model.minimize(sum(v))
    return mathopt.solve(model, mathopt.SolverType.GLOP).objective_value()


if __name__ == "__main__":
    print(total_violation([([1, 1], "<=", 10), ([1, 0], ">=", 2)]))
    print(total_violation([([1, 1], "<=", 10), ([1, 1], ">=", 12)]))
