"""Lesson 9.2.3: the exact step points of the budget-value curve V(B), found by two solves per step.

V(B) is the best NPV of the selection model (selection.py) with budget B. It only moves when B
reaches the cost of a plan worth more than V(B), so the next step after level v is the cheapest plan
worth at least v + 1 (NPVs are whole $k). GridCap is fictional.
"""

from __future__ import annotations

from ortools.math_opt.python import mathopt

from gridcap import Portfolio, generate
from selection import best_value, build, solve_highs


def cheapest_reaching(portfolio: Portfolio, level: int) -> int | None:
    """min cost  s.t.  value >= level and every selection rule: where V(B) first reaches `level`."""
    sel = build(portfolio, 0)
    sel.model.delete_linear_constraint(sel.budget)
    sel.model.add_linear_constraint(sel.value >= level, name="reach")
    sel.model.minimize(sel.cost)
    result = solve_highs(sel.model)
    if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
        return None                                   # no plan is worth that much
    return round(result.objective_value())


def step_points(portfolio: Portfolio, lo: int, hi: int) -> list[tuple[int, int]]:
    """Every (B, V(B)) in [lo, hi] where V steps up, starting with (lo, V(lo))."""
    points = [(lo, best_value(portfolio, lo))]
    while True:
        budget = cheapest_reaching(portfolio, points[-1][1] + 1)
        if budget is None or budget > hi:
            return points
        points.append((budget, best_value(portfolio, budget)))   # V(budget) can pass level + 1


if __name__ == "__main__":
    small = generate("small")
    must_cost = sum(p.capex for p in small.projects if p.must_do)
    points = step_points(small, must_cost, sum(p.capex for p in small.projects))
    print(f"must-do cost {must_cost:,}: V = {points[0][1]:,}; the curve steps {len(points) - 1:,} times "
          f"and stops at B = {points[-1][0]:,}, V = {points[-1][1]:,}")
    print("first steps:", points[:5])
    rises = [(points[k + 1][1] - points[k][1], points[k + 1][0]) for k in range(len(points) - 1)]
    flats = [(points[k + 1][0] - points[k][0], points[k][0]) for k in range(len(points) - 1)]
    print(f"largest rise {max(rises)[0]:,} at B = {max(rises)[1]:,}; "
          f"longest flat stretch {max(flats)[0]:,} from B = {max(flats)[1]:,}")
    print(f"median distance between steps: {sorted(f for f, _ in flats)[len(flats) // 2]:,}")
