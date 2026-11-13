"""Compare one solver's settings with its defaults on the regional plans, on two measures at once.

The instance set is `plan_model.instance_set()`, fixed before any run. Each (instance, seed) is one
paired observation. For each setting the report gives, against the default:
- work to a plan within 1% of the instance's optimum (the side of the gap a planner sees first);
- work to prove optimality (the side that ends the solve);
each as a ratio of shifted geometric means, with the count of observations where the setting needed
less and more work. A ratio below 1 means less work than the default.
"""

from __future__ import annotations

import math

from plan_model import instance_set
from runs import Run
from sgm import compare


def run_all(solve, settings: dict, seeds: tuple[int, ...]) -> dict[tuple[str, int, str], Run]:
    """solve(portfolio, seed, setting) for every instance, seed and named setting."""
    return {(pf.name, seed, name): solve(pf, seed, setting)
            for pf in instance_set() for seed in seeds for name, setting in settings.items()}


def report(runs: dict[tuple[str, int, str], Run], shift: float, unit: str) -> None:
    best: dict[str, float] = {}
    for (name, _, _), r in runs.items():
        if r.status == "optimal":
            best[name] = max(best.get(name, -math.inf), r.objective)
    pairs = sorted({(name, seed) for name, seed, _ in runs})
    settings = list(dict.fromkeys(key[2] for key in runs))
    print(f"{'setting':<22} {'solved':>6}  {'to 1%':>6} {'W/L':>6}  {'to proof':>8} {'W/L':>6}")
    for s in settings:
        mine = [runs[n, seed, s] for n, seed in pairs]
        base = [runs[n, seed, "default"] for n, seed in pairs]
        r1, w1, l1 = compare([r.within(best[r.instance], 0.01) for r in mine],
                             [r.within(best[r.instance], 0.01) for r in base], shift)
        rp, wp, lp = compare([r.work for r in mine], [r.work for r in base], shift)
        solved = sum(r.status == "optimal" for r in mine)
        print(f"{s:<22} {solved:>3}/{len(mine):<2}  {r1:>6.2f} {w1:>2}/{l1:<3}  {rp:>8.2f} {wp:>2}/{lp:<3}")
    print(f"({len(pairs)} paired observations; ratios of shifted geometric means of work in {unit}, "
          f"shift {shift:g}; W/L: less/more work than the default)")
