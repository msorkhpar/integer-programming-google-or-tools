"""Lesson 6.6.4: the five-breakpoint value curve of each GridCap small asset with a replacement project.

GridCap is a fictional utility's portfolio. For each candidate the program prints the asset's age
and Weibull shape, its value curve at depths 0, 0.25, 0.5, 0.75 and 1 ($k avoided over the plan),
the curve's shape, and how far the five-point curve is from the true one at the worst depth.
"""

from gridcap import generate
from lifecycle import DEPTHS, candidates, risk_avoided, value_curve


def worst_gap(asset, curve, steps: int = 400) -> float:
    """The largest |true value - curve value| over a fine grid of depths, in $k."""
    return max(abs(risk_avoided(asset, k / steps) - curve(k / steps)) for k in range(steps + 1))


if __name__ == "__main__":
    small = generate("small")
    print("project asset        age  beta | value at depth " + "  ".join(f"{d:4}" for d in DEPTHS)
          + " | shape   | capex | worst gap")
    for p, a in candidates(small):
        curve = value_curve(a)
        shape = "concave" if curve.concave() else "convex" if curve.convex() else "neither"
        print(f"{p.project_id}    {a.kind:11} {a.age:3} {a.weibull_beta:5} |               "
              + "  ".join(f"{v:4.0f}" for v in curve.ys) + f" | {shape:7} | {p.capex:5} | {worst_gap(a, curve):5.1f}")
    a = small.asset("A019")
    nine = value_curve(a, tuple(k / 8 for k in range(9)))
    print(f"A019 with 9 breakpoints: worst gap {worst_gap(a, nine):.1f} (5 breakpoints: {worst_gap(a, value_curve(a)):.1f})")
