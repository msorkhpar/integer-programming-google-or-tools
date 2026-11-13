"""Lesson 9.2.4: what the next $k of budget is worth to the MILP, against the LP relaxation's price.

For each budget B: the LP relaxation's budget price, and the MILP's real gain V(B + d) - V(B) read off
the exact step points in [B, B + 1,000] (step_points.py). GridCap is fictional.
"""

from bisect import bisect_right

from gridcap import generate
from selection import build, clean, solve_glop
from step_points import step_points

small = generate("small")


def value_at(points: list[tuple[int, int]], budget: int) -> int:
    """V(budget) from step points: the value of the last step at or below the budget."""
    return points[bisect_right([b for b, _ in points], budget) - 1][1]


def lp_price(budget: int) -> float:
    lp = build(small, budget, integer=False)
    return solve_glop(lp.model).dual_values(lp.budget)


print(f"{'B':<6} {'price':>6} | {'gain':>4} {'gain':>4} {'gain':>5} {'p x':>5} {'gain':>5} {'p x':>5} | {'next':>6} {'rise':>4}")
print(f"{'':<6} {'p':>6} | {'+1':>4} {'+10':>4} {'+100':>5} {'100':>5} {'+1000':>5} {'1000':>5} | {'step':>6}")
for B in (20000, 30000, 38390, 45000, 50000, 60000):
    points = step_points(small, B, B + 1000)
    p = lp_price(B)
    gain = {d: value_at(points, B + d) - points[0][1] for d in (1, 10, 100, 1000)}
    print(f"{B:<6} {clean(p):>6} | {gain[1]:>4} {gain[10]:>4} {gain[100]:>5} {p * 100:>5.0f} {gain[1000]:>5} "
          f"{p * 1000:>5.0f} | {points[1][0]:>6} {points[1][1] - points[0][1]:>4}")


def sentence(budget: int, points: list[tuple[int, int]], window: int) -> str:
    """What the next dollars are worth, in words a planner can check against the step points."""
    (b0, v0), (b1, v1) = points[0], points[1]
    gain = value_at(points, budget + window) - v0
    return (f"At ${budget:,}k the plan is worth ${v0:,}k. Extra budget buys nothing until ${b1:,}k, "
            f"where the value rises by ${v1 - v0:,}k. ${window:,}k more is worth ${gain:,}k in all, "
            f"over {len([b for b, _ in points if budget < b <= budget + window])} separate steps.")


print()
print(sentence(38390, step_points(small, 38390, 39390), 1000))
