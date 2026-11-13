from __future__ import annotations

from ortools.math_opt.python import mathopt

EXACT = mathopt.SolveParameters(relative_gap_tolerance=0.0)


def sweep(costs: list[int], values: list[int], must: list[int], budgets: list[int]) -> list[tuple[int, int | None]]:
    """The best total value at each budget, or None where no plan meets the rules."""
    # TODO: write the formulation for one budget, then solve it at each budget.
    return [(b, 0) for b in budgets]


if __name__ == "__main__":
    print(sweep([2, 3, 4], [6, 6, 4], [], [0, 2, 5, 9]))
