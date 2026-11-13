"""Lesson 6.6.4: a renewal fund spread across GridCap small's candidates, on their value curves.

GridCap is a fictional utility's portfolio; the renewal fund and partial renewals are invented
(see lifecycle.py). The program writes every curve as segments, every curve in the incremental
form, and each curve by its shape, then compares what each model claims with the true value of the
depths it chose, and solves once more with nine breakpoints per curve.
"""

from gridcap import generate
from lifecycle import candidates, renewal_model, risk_avoided, by_shape
from piecewise import add_incremental, add_segments, value
from selection import EXACT, solve_highs

FUND = 3000                                       # $k for renewals this plan


def report(label, portfolio, choose, depths=None):
    plan = renewal_model(portfolio, FUND, choose, **({"depths": depths} if depths else {}))
    result = solve_highs(plan.model, EXACT)
    chosen = {pid: value(result, d) for pid, d in plan.depth.items()}
    true = sum(risk_avoided(asset, chosen[p.project_id]) for p, asset in candidates(portfolio))
    print(f"{label}: {plan.binaries:2} binaries, claims ${result.objective_value():,.1f}k, "
          f"true value ${true:,.1f}k")
    print("    depths:", {pid: round(d, 3) for pid, d in chosen.items() if d > 1e-6})


if __name__ == "__main__":
    small = generate("small")
    print(f"renewal fund ${FUND:,}k, {len(candidates(small))} candidates")
    report("segments for every curve  ", small, lambda curve: add_segments)
    report("incremental for every curve", small, lambda curve: add_incremental)
    report("chosen by each curve's shape", small, by_shape)
    report("by shape, 9 breakpoints    ", small, by_shape, tuple(k / 8 for k in range(9)))
