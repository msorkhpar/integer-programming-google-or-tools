"""Lesson 9.2.3: the budget-value curve from repeated solves on a grid, and from its exact step points.

GridCap is fictional. The window is $38,000k to $39,000k, around the small portfolio's capital budget.
"""

from gridcap import generate
from selection import best_value, build, solve_glop
from step_points import step_points

small = generate("small")
LO, HI = 38000, 39000


def lp_value(budget: int) -> float:
    return solve_glop(build(small, budget, integer=False).model).objective_value()


# A grid sweep: one MILP solve per budget.
for step in (250, 50):
    grid = [(b, best_value(small, b)) for b in range(LO, HI + 1, step)]
    levels = sorted({v for _, v in grid})
    print(f"grid every {step:>3}: {len(grid):>2} solves, {len(levels):>2} distinct values")
    if step == 250:
        print("   ", grid)

# The exact curve: every step point in the window.
points = step_points(small, LO, HI)
print(f"exact: {len(points) - 1} steps in [{LO:,}, {HI:,}]")
print(f"{'B':>7} {'V(B)':>7} {'rise':>5} {'LP(B)':>9}")
for k, (b, v) in enumerate(points[:12]):
    rise = v - points[k - 1][1] if k else 0
    print(f"{b:>7,} {v:>7,} {rise:>5} {lp_value(b):>9,.1f}")
print("   ...")
print(f"{points[-1][0]:>7,} {points[-1][1]:>7,}")
rises = [v - u for (_, u), (_, v) in zip(points, points[1:])]
flats = [b - a for (a, _), (b, _) in zip(points, points[1:])]
print(f"all {len(rises)} steps: rise {min(rises)} to {max(rises)}, flat stretch {min(flats)} to {max(flats)}")

# Where a step lands, a grid point can only bracket it.
b, v = points[5]
print(f"\nV({b - 1:,}) = {best_value(small, b - 1):,}, V({b:,}) = {best_value(small, b):,}: the step is at {b:,} exactly")
