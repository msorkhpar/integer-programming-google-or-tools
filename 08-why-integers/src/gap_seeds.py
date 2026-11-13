"""The integrality gap over ten seeds of each GridCap size: it shrinks as the portfolio grows."""

from statistics import median

from gridcap import generate
from gap_by_size import integrality_gap
from selection import best_plan, lp_values

if __name__ == "__main__":
    for size in ("tiny", "small", "medium"):
        gaps, absolute = [], []
        for seed in range(1, 11):
            portfolio = generate(size, seed)
            lp_bound, _ = lp_values(portfolio)
            optimum, _ = best_plan(portfolio)
            gaps.append(integrality_gap(lp_bound, optimum))
            absolute.append(lp_bound - optimum)
        print(f"{size:<7} gap min {min(gaps):.3%}  median {median(gaps):.3%}  max {max(gaps):.3%}   "
              f"abs gap median {median(absolute):,.0f}")
