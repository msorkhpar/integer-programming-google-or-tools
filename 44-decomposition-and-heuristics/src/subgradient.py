"""Subgradient optimization of the budget prices, with a repaired plan as the lower bound."""

from __future__ import annotations

from gridcap import Portfolio, generate

from capital import EXACT, build, solve_highs, value, violations
from lagrange import lagrangian, spend_of


def repair(portfolio: Portfolio, plan: dict[str, int]) -> dict[str, int]:
    """Make a relaxed plan fit the budgets: drop the cheapest-per-dollar projects, then refill."""
    plan = dict(plan)
    by_id = {p.project_id: p for p in portfolio.projects}
    while over := [y for y, s in spend_of(portfolio, plan).items() if s > portfolio.budget[y]]:
        droppable = [pid for pid in plan if not by_id[pid].must_do
                     and not any(by_id[c].parent == pid for c in plan)]
        worst = min(droppable, key=lambda pid: by_id[pid].npv[plan[pid]]
                    / (1 + sum(c for y, c in by_id[pid].spend(plan[pid]).items() if y in over)))
        del plan[worst]
    for p in sorted(portfolio.projects, key=lambda p: -p.value / p.capex):
        if p.project_id in plan:
            continue
        for t in sorted(p.starts(), key=lambda t: -p.npv[t]):
            if not violations(portfolio, {**plan, p.project_id: t}):
                plan[p.project_id] = t
                break
    return plan


def subgradient(portfolio: Portfolio, iterations: int = 60, theta: float = 2.0, patience: int = 5):
    lam = {y: 0.0 for y in portfolio.years}
    best_bound, best_plan, best_value = float("inf"), {}, -float("inf")
    stalled, history = 0, []
    for k in range(1, iterations + 1):
        bound, relaxed = lagrangian(portfolio, lam)
        plan = repair(portfolio, relaxed)
        if value(portfolio, plan) > best_value:
            best_plan, best_value = plan, value(portfolio, plan)
        if bound < best_bound - 1e-6:
            best_bound, stalled = bound, 0
        else:
            stalled += 1
            if stalled >= patience:
                theta, stalled = theta / 2, 0
        spend = spend_of(portfolio, relaxed)
        g = {y: portfolio.budget[y] - spend[y] for y in portfolio.years}   # a subgradient of L at lam
        norm = sum(v * v for v in g.values())
        history.append((k, bound, best_bound, best_value, dict(lam)))
        if norm == 0:
            break
        step = theta * (bound - best_value) / norm                            # Polyak's step
        lam = {y: max(0.0, lam[y] - step * g[y]) for y in portfolio.years}
    return best_bound, best_plan, history


if __name__ == "__main__":
    small = generate("small")
    best_bound, plan, history = subgradient(small)
    for k, bound, best, feasible, lam in history:
        if k in (1, 2, 3, 5, 10, 20, 30, 40, 50, 60) or k == len(history):
            prices = " ".join(f"{lam[y]:.3f}" for y in small.years)
            print(f"iter {k:2}  L(lam) {bound:9,.1f}  best bound {best:9,.1f}  best plan {feasible:7,}"
                  f"  gap {100 * (best - feasible) / feasible:5.2f}%  lam {prices}")
    milp = solve_highs(build(small).model, EXACT)
    relaxed_lp = build(small, integer=False)
    lp = solve_highs(relaxed_lp.model)
    print(f"MILP optimum {milp.objective_value():9,.1f}   LP bound {lp.objective_value():9,.1f}")
    print(f"Lagrangian bound - optimum {best_bound - milp.objective_value():8,.1f}"
          f"   repaired plan breaks: {violations(small, plan) or 'nothing'}")
    duals = " ".join(f"{lp.dual_values(relaxed_lp.budget[y]):.3f}" for y in small.years)
    print(f"LP budget-row duals {duals}")
