"""Fund the riskiest assets first, or choose the plan that removes the most risk within the rules."""

from itertools import combinations

from asset_risk import expected_failure_cost, tiny
from greedy_vs_best import allowed, by_id

#: How much younger an intervention makes its asset: a replacement makes it new.
AGE_AFTER = {"replace": 0.0, "rebuild": 0.0, "underground": 0.0, "repair": 0.5, "trim": 0.5,
             "clear": 0.5, "widen": 0.5}


def risk_avoided(project) -> float:
    asset = tiny.asset(project.asset_id)
    after = asset.age * AGE_AFTER[project.intervention]
    return expected_failure_cost(asset) - expected_failure_cost(asset, after)


def avoided(plan: set[str]) -> float:
    return sum(risk_avoided(by_id[i]) for i in plan)


def riskiest_first() -> set[str]:
    plan: set[str] = set()
    for p in sorted(tiny.projects, key=lambda p: expected_failure_cost(tiny.asset(p.asset_id)), reverse=True):
        if sum(by_id[i].capex for i in plan) + p.capex <= tiny.capital_budget:
            plan.add(p.project_id)
    return plan


def most_risk_avoided() -> set[str]:
    best = None
    for k in range(len(by_id) + 1):
        for combo in combinations(by_id, k):
            plan = set(combo)
            if allowed(plan) and (best is None or avoided(plan) > avoided(best)):
                best = plan
    return best


if __name__ == "__main__":
    for p in tiny.projects:
        print(f"{p.project_id} {p.intervention:11} risk avoided {risk_avoided(p):6.1f} $k/yr  capex {p.capex:>5,}")
    ranked, best = riskiest_first(), most_risk_avoided()
    print("riskiest first ", sorted(ranked), f"avoids {avoided(ranked):.1f}", "allowed" if allowed(ranked) else "breaks a rule")
    print("most avoided   ", sorted(best), f"avoids {avoided(best):.1f}", "allowed" if allowed(best) else "breaks a rule")
