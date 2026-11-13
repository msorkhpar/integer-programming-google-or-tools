"""Lesson 6.5.3: "do nothing" as an explicit alternative, priced by the asset's risk.

GridCap is a fictional utility's portfolio. The risk of leaving an asset alone is the chance it
fails in the plan's five years, given its age (lesson 1.1.2), times its consequence of failure.
"""

import math
from dataclasses import replace

from gridcap import generate
from planning_model import build, groups_of, money, schedule, solve_highs

small = generate("small")
groups = groups_of(small)
HORIZON = len(small.years)


def pof_within(asset, years: int) -> float:
    """Chance the asset fails within `years`, given that it has survived to its age (Weibull)."""
    now = (asset.age / asset.weibull_eta) ** asset.weibull_beta
    later = ((asset.age + years) / asset.weibull_eta) ** asset.weibull_beta
    return 1 - math.exp(-(later - now))


risk = {}
for g, members in groups.items():
    asset = small.asset(small.project(members[0]).asset_id)
    risk[g] = round(pof_within(asset, HORIZON) * asset.cof)
    print(f"{g} {asset.asset_id}: age {asset.age}, PoF in {HORIZON} years {pof_within(asset, HORIZON):.3f}, "
          f"CoF {money(asset.cof)}, risk of doing nothing {money(risk[g])}")


def solve(portfolio, price_risk: bool):
    plan = build(portfolio)
    keep = {}
    for g, members in groups.items():
        keep[g] = plan.model.add_binary_variable(name=f"keep_{g}")
        plan.model.add_linear_constraint(sum(plan.started(i) for i in members) + keep[g] == 1,
                                         name=f"choose_{g}")
    if price_risk:
        npv = plan.model.objective.as_linear_expression()
        plan.model.maximize(npv - sum(risk[g] * keep[g] for g in groups))
    result = solve_highs(plan.model)
    starts = schedule(plan, result)
    picks = {}
    for g, members in groups.items():
        done = [f"{i} {small.project(i).intervention} {starts[i]}" for i in members if i in starts]
        picks[g] = done[0] if done else "keep (do nothing)"
    npv = sum(small.project(i).npv[t] for i, t in starts.items())
    return result.objective_value(), npv, picks


cut = replace(small, budget={**small.budget, 2027: 6_000})
for budgets, portfolio in [("generated budgets", small), ("2027 cut to $6,000k", cut)]:
    print(budgets)
    for label, price in [("NPV only", False), ("NPV - risk", True)]:
        objective, npv, picks = solve(portfolio, price)
        print(f"  {label:10}  objective {money(objective)}  NPV {money(npv)}  {picks}")
