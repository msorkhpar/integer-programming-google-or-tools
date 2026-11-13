"""A 0-1 knapsack branch-and-bound in plain Python, with no solver.

The LP relaxation of a knapsack has one row, so it needs no LP solver: fill the budget with the
best value per dollar first and take a fraction of the first item that does not fit. That is
Dantzig's bound. The search around it is the branch-and-bound of lessons 3.2.1 to 3.2.3:
depth-first, branching on the one fractional item, pruning by infeasibility, integrality and bound.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from gridcap import Portfolio


@dataclass(frozen=True)
class Item:
    name: str
    value: int         # what funding it is worth, $k
    cost: int          # what it costs, $k (more than 0)


def by_ratio(items: list[Item]) -> list[Item]:
    """Best value per dollar first; ties by name, so every run takes the same path."""
    return sorted(items, key=lambda it: (-it.value / it.cost, it.name))


@dataclass(frozen=True)
class Relaxed:
    value: float                   # the LP value: no plan with these items fixed is worth more
    taken: dict[str, float]        # item -> its value in the LP solution, 0 < v <= 1
    split: str | None              # the item taken in part, or None when the LP solution is whole


def dantzig_bound(items: list[Item], budget: int, fixed: dict[str, int]) -> Relaxed | None:
    """The LP relaxation with `fixed` items held at 0 or 1. `items` must be in ratio order.

    None when the items fixed at 1 already cost more than the budget.
    """
    left = budget - sum(it.cost for it in items if fixed.get(it.name) == 1)
    if left < 0:
        return None
    value = float(sum(it.value for it in items if fixed.get(it.name) == 1))
    taken = {it.name: 1.0 for it in items if fixed.get(it.name) == 1}
    for it in items:
        if it.name in fixed:
            continue
        if it.cost <= left:
            left -= it.cost
            value += it.value
            taken[it.name] = 1.0
        else:
            share = left / it.cost
            if share > 0:
                value += share * it.value
                taken[it.name] = share
                return Relaxed(value, taken, it.name)
            return Relaxed(value, taken, None)
    return Relaxed(value, taken, None)


@dataclass
class Result:
    value: int = -1                                  # the best plan's value; -1 until one is found
    plan: list[str] = field(default_factory=list)
    nodes: int = 0
    pruned: dict[str, int] = field(default_factory=lambda: {"infeasible": 0, "bound": 0, "integral": 0})


def solve(items: list[Item], budget: int, log: list[str] | None = None) -> Result:
    """The most valuable set of items whose costs fit the budget. `log`, if given, gets one line per node."""
    order = by_ratio(items)
    result = Result()
    stack: list[dict[str, int]] = [{}]
    while stack:
        fixed = stack.pop()
        result.nodes += 1
        lp = dantzig_bound(order, budget, fixed)
        if lp is None:
            result.pruned["infeasible"] += 1
            action = "infeasible"
        elif math.floor(lp.value + 1e-9) <= result.value:      # values are whole $k
            result.pruned["bound"] += 1
            action = f"bound {lp.value:,.1f} cannot beat {result.value:,}"
        elif lp.split is None:
            result.pruned["integral"] += 1
            result.value, result.plan = round(lp.value), sorted(lp.taken)
            action = f"integral: new incumbent {result.value:,}"
        else:
            stack.append({**fixed, lp.split: 0})
            stack.append({**fixed, lp.split: 1})                 # popped first: dive on taking it
            action = f"bound {lp.value:,.1f}, branch on {lp.split} = {lp.taken[lp.split]:.3f}"
        if log is not None:
            log.append(f"{result.nodes:>2} {' '.join(f'{k}={v}' for k, v in fixed.items()) or 'root':<26} {action}")
    return result


def brute_force(items: list[Item], budget: int) -> int:
    """The best value by trying all 2^n plans: the check for small n."""
    best = 0
    for mask in range(1 << len(items)):
        chosen = [it for k, it in enumerate(items) if mask >> k & 1]
        if sum(it.cost for it in chosen) <= budget:
            best = max(best, sum(it.value for it in chosen))
    return best


def gridcap_knapsack(portfolio: Portfolio) -> tuple[list[Item], int, list[str]]:
    """The budget-only selection: must-dos are funded first, the rest compete for what is left.

    Returns the discretionary items, the budget left for them, and the must-do project ids.
    """
    must = [p for p in portfolio.projects if p.must_do]
    items = [Item(p.project_id, p.value, p.capex) for p in portfolio.projects if not p.must_do]
    return items, portfolio.capital_budget - sum(p.capex for p in must), [p.project_id for p in must]
