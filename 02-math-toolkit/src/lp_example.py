"""OR-Tools' small LP example: GLOP's answer, and every vertex of its feasible region."""
# Adapted from the OR-Tools example "Solving an LP Problem", https://developers.google.com/optimization/lp/lp_example

import itertools

import numpy as np
from ortools.math_opt.python import mathopt

names = ["c1", "c2", "c3", "x_nonneg", "y_nonneg"]
A = np.array([[1, 2],      # x + 2y <= 14
              [-3, 1],     # 3x - y >= 0, written -3x + y <= 0
              [1, -1],     # x - y <= 2
              [-1, 0],     # x >= 0
              [0, -1]])    # y >= 0
b = np.array([14, 0, 2, 0, 0])
c = np.array([3, 4])


def solve_with_glop() -> tuple[str, float, float, float]:
    model = mathopt.Model(name="lp-example")
    x = model.add_variable(lb=0, name="x")
    y = model.add_variable(lb=0, name="y")
    model.add_linear_constraint(x + 2 * y <= 14, name="c1")
    model.add_linear_constraint(3 * x - y >= 0, name="c2")
    model.add_linear_constraint(x - y <= 2, name="c3")
    model.maximize(3 * x + 4 * y)
    result = mathopt.solve(model, mathopt.SolverType.GLOP)
    return (result.termination.reason.name, result.objective_value(),
            result.variable_values(x), result.variable_values(y))


def vertices() -> list[tuple[np.ndarray, list[str]]]:
    """Every feasible crossing of two rows, once each, with all the rows tight there."""
    found: list[tuple[np.ndarray, list[str]]] = []
    for i, k in itertools.combinations(range(len(b)), 2):
        pair = A[[i, k]]
        if abs(np.linalg.det(pair)) < 1e-12:
            continue
        point = np.linalg.solve(pair, b[[i, k]]) + 0.0
        if np.all(A @ point <= b + 1e-9) and not any(np.allclose(point, q) for q, _ in found):
            tight = [n for n, t in zip(names, np.abs(A @ point - b) <= 1e-9) if t]
            found.append((point, tight))
    return found


if __name__ == "__main__":
    status, value, x, y = solve_with_glop()
    print(f"GLOP: {status}, (x, y) = ({x:.1f}, {y:.1f}), objective {value:.1f}")
    for point, tight in vertices():
        print(f"  vertex (x, y) = ({point[0]:.0f}, {point[1]:.0f})  objective {c @ point:>2.0f}  tight {tight}")
