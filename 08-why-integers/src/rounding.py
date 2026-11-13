"""Round GridCap small's LP relaxation up, to the nearest whole, and down, and check each plan."""

from gridcap import generate
from selection import best_plan, broken_rows, cost, lp_values, value

small = generate("small")
EPS = 1e-6

RULES = {
    "up": lambda v: v > EPS,              # any share at all becomes a funded project
    "nearest": lambda v: v >= 0.5,
    "down": lambda v: v > 1 - EPS,        # only projects the LP funded whole
}


def rounded(values: dict[str, float], how: str) -> set[str]:
    return {pid for pid, v in values.items() if RULES[how](v)}


def fill(portfolio, plan: set[str]) -> set[str]:
    """Add projects best value per dollar first, each only if it fits and keeps every rule."""
    plan = set(plan)
    for p in sorted(portfolio.projects, key=lambda p: p.value / p.capex, reverse=True):
        if p.project_id not in plan and not broken_rows(portfolio, plan | {p.project_id}):
            plan.add(p.project_id)
    return plan


if __name__ == "__main__":
    lp_value, values = lp_values(small)
    print(f"budget {small.capital_budget:,}  LP bound {lp_value:,.2f}")
    for how in RULES:
        plan = rounded(values, how)
        print(f"{how:>7}: spend {cost(small, plan):,}, value {value(small, plan):,}, breaks {broken_rows(small, plan)}")
    best_value, best = best_plan(small)
    down = rounded(values, "down")
    print(f"optimum: spend {cost(small, best):,}, value {best_value:,.0f}, breaks {broken_rows(small, best)}")
    print(f"  in the optimum, not in round-down: {sorted(best - down)}")
    print(f"  in round-down, not in the optimum: {sorted(down - best)}")
    filled = fill(small, down)
    print(f"round down, then fill: adds {sorted(filled - down)}, value {value(small, filled):,}, "
          f"{best_value - value(small, filled):,.0f} short of the optimum")
