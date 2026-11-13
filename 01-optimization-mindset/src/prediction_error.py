"""If the PoF model is wrong about distribution assets, does the best plan change?"""

from itertools import combinations

from asset_risk import next_year_pof, tiny
from greedy_vs_best import allowed, by_id
from rank_vs_optimize import AGE_AFTER


def best_plan(scale: float) -> set[str]:
    def avoided(i: str) -> float:
        p = by_id[i]
        a = tiny.asset(p.asset_id)
        now = next_year_pof(a.age, a.weibull_beta, a.weibull_eta)
        after = next_year_pof(a.age * AGE_AFTER[p.intervention], a.weibull_beta, a.weibull_eta)
        factor = scale if p.program == "distribution" else 1.0
        return (now - after) * factor * a.cof

    best, best_value = None, None
    for k in range(len(by_id) + 1):
        for combo in combinations(by_id, k):
            plan = set(combo)
            score = sum(avoided(i) for i in plan)
            if allowed(plan) and (best is None or score > best_value):
                best, best_value = plan, score
    return best


if __name__ == "__main__":
    for scale in (0.3, 0.5, 1.0, 2.0):
        print(f"distribution PoF x{scale}: best plan {sorted(best_plan(scale))}")
