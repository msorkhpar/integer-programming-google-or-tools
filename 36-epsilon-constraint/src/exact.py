"""The exact frontier of GridCap small: NPV as the floor in $1k steps, AUGMECON with jump and early exit.

Then the same frontier again with no reward, two passes per floor, to check the condition the reward
needs here: risk is not whole $k, so nothing promises by construction that the reward never trades
risk for slack.
"""

from ortools.math_opt.python import mathopt

from frontier import best_of, dominated, exact_frontier, score, supported
from gridcap import generate
from objectives import build

small = generate("small")
two = build(small)

points, solves = exact_frontier(two.model, two.risk, two.npv, step=1)
print(f"{len(points)} Pareto-optimal plans in {solves} ε solves (plus 4 for the payoff table)")
print(f"pairs where one plan dominates another: {len(dominated(points))}")
print(f"supported (a weighted sum finds them): {len(supported(points))}; unsupported: "
      f"{len(points) - len(supported(points))}")
print("first five, by NPV:", ", ".join(f"({p.second:,.0f}, {p.first:,.0f})" for p in points[:5]))


def two_pass_frontier(model, first, second) -> list:
    """Every Pareto point with no reward: at each floor the most `first`, then the most `second` at it."""
    found, floor = [], None
    while True:
        row = None if floor is None else model.add_linear_constraint(second >= floor, name="eps_floor")
        result = best_of(model, first, then=second)
        if row is not None:
            model.delete_linear_constraint(row)
        if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
            return found
        found.append(score(first, second, result.variable_values()))
        floor = round(found[-1].second) + 1                  # NPV is whole $k: the next point has more


def key(p) -> tuple[float, float]:
    return round(p.first, 3), round(p.second, 3)


check = two_pass_frontier(two.model, two.risk, two.npv)
risks = sorted(key(p)[0] for p in points)
gap = min(b - a for a, b in zip(risks, risks[1:]))
print(f"two passes per floor, no reward: {len(check)} plans; the same as AUGMECON's: "
      f"{sorted(map(key, check)) == sorted(map(key, points))}")
print(f"closest neighbours differ by ${gap * 1000:,.0f} of risk; the reward is at most $1 (0.001 of $1k)")
