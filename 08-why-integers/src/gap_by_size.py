"""The LP bound, the optimum and the integrality gap of the selection model on three GridCap sizes."""

from gridcap import generate
from selection import best_plan, lp_values


def integrality_gap(lp_bound: float, optimum: float) -> float:
    """How far above the best plan the LP bound sits, as a share of the best plan (maximizing)."""
    return (lp_bound - optimum) / abs(optimum)


if __name__ == "__main__":
    print(f"{'size':<7}{'projects':>9}{'LP bound':>13}{'optimum':>11}{'abs gap':>10}{'gap':>9}")
    for size in ("tiny", "small", "medium"):
        portfolio = generate(size)
        lp_bound, _ = lp_values(portfolio)
        optimum, _ = best_plan(portfolio)
        print(f"{size:<7}{len(portfolio.projects):>9}{lp_bound:>13,.2f}{optimum:>11,.0f}"
              f"{lp_bound - optimum:>10,.2f}{integrality_gap(lp_bound, optimum):>9.3%}")
