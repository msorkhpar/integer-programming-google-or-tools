"""Rounding the LP relaxation on 30 GridCap small portfolios: which rows break, and what it costs."""

from statistics import mean

from gridcap import generate
from rounding import RULES, rounded
from selection import best_plan, broken_rows, lp_values, value

SEEDS = range(1, 31)

if __name__ == "__main__":
    broke = {how: {"budget": 0, "alt": 0} for how in RULES}
    loss = []
    for seed in SEEDS:
        portfolio = generate("small", seed)
        _, values = lp_values(portfolio)
        best_value, _ = best_plan(portfolio)
        for how in RULES:
            rows = broken_rows(portfolio, rounded(values, how))
            broke[how]["budget"] += "budget" in rows
            broke[how]["alt"] += any(r.startswith("alt_") for r in rows)
        loss.append(100 * (best_value - value(portfolio, rounded(values, "down"))) / best_value)
    print(f"{len(SEEDS)} small portfolios (seeds {SEEDS.start}-{SEEDS.stop - 1})")
    for how, counts in broke.items():
        print(f"{how:>7}: broke the budget in {counts['budget']:2}, an alternative group in {counts['alt']}")
    print(f"round down below the optimum: mean {mean(loss):.1f}%, worst {max(loss):.1f}%")
