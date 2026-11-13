from __future__ import annotations

from ortools.math_opt.python import mathopt


def plan_spending(budgets: dict[int, float], work: dict[int, float], value: dict[int, float], max_carry: float):
    """Spend each year's budget, with carry-over into the next year. Returns (status, value, spend, carry)."""
    # TODO: spend and carry variables with their bounds, one cash row per year, the objective,
    # a GLOP solve, and the status before any value.
    return "NOT_SOLVED", None, None, None

if __name__ == "__main__":
    print(plan_spending({2030: 100, 2031: 100}, {2030: 60, 2031: 150}, {2030: 1.0, 2031: 0.9}, 0.5))
