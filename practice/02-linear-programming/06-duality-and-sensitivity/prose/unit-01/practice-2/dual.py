from __future__ import annotations

import math

from ortools.math_opt.python import mathopt


def solve_dual(value: dict[str, float],
               rows: dict[str, tuple[dict[str, float], str, float]]) -> tuple[float | None, dict[str, float]]:
    """Build and solve the dual of the maximization LP; return its optimal value and the row prices."""
    # TODO: write the dual on paper first: one price per row (its sign set by the row's sense),
    # one cover row per activity, and the objective. Then build it, solve it with GLOP, and read it.
    return 0.0, {}


if __name__ == "__main__":
    value = {"inspect": 4, "repair": 3}
    rows = {"hours": ({"inspect": 1, "repair": 1}, "<=", 10), "inspect_cap": ({"inspect": 1}, "<=", 6)}
    print(solve_dual(value, rows))
