"""Lesson 3.2.2: start the search with a plan already in hand, and count the nodes it saves."""

from bnb import branch_and_bound
from gridcap import generate
from selection import build, solve_lp

for size in ("tiny", "small"):
    portfolio = generate(size)
    sel = build(portfolio)
    root = solve_lp(sel, fixed={})
    plan = [pid for pid, v in root.x.items() if v > 1 - 1e-6]          # round the root LP down
    value = sum(portfolio.project(pid).value for pid in plan)
    cost = sum(portfolio.project(pid).capex for pid in plan)
    print(f"{size}: root LP rounded down funds {len(plan)} projects, cost {cost:,} of {portfolio.capital_budget:,},"
          f" value {value:,}")
    cold = branch_and_bound(sel)
    warm = branch_and_bound(sel, start=(value, plan))
    print(f"  no starting plan:     {len(cold.steps):>4} nodes, best {cold.value:,.0f}")
    print(f"  rounded plan to beat: {len(warm.steps):>4} nodes, best {warm.value:,.0f}")
