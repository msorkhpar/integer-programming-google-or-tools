from __future__ import annotations

from ortools.math_opt.python import mathopt


def total_violation(rows: list[tuple[list[float], str, float]]) -> float:
    """The least total stretch v_r >= 0 that lets some x >= 0 satisfy every row."""
    # TODO: variables x_j >= 0 and v_r >= 0; each "<=" row as a.x - v_r <= b, each ">=" row as
    # a.x + v_r >= b; minimize the sum of the v_r with GLOP and return the objective value.
    return -1.0


if __name__ == "__main__":
    print(total_violation([([1, 1], "<=", 10), ([1, 0], ">=", 2)]))
    print(total_violation([([1, 1], "<=", 10), ([1, 1], ">=", 12)]))
