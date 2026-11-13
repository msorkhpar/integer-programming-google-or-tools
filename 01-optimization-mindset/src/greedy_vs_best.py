"""Fund the best value per dollar first, then compare with the best of all 256 plans."""

from itertools import combinations

from gridcap import generate

tiny = generate("tiny")
budget = tiny.capital_budget
by_id = {p.project_id: p for p in tiny.projects}


def allowed(plan: set[str]) -> bool:
    if sum(by_id[i].capex for i in plan) > budget:
        return False
    if any(p.must_do and p.project_id not in plan for p in tiny.projects):
        return False
    if any(by_id[i].parent and by_id[i].parent not in plan for i in plan):
        return False
    groups = [by_id[i].alt_group for i in plan if by_id[i].alt_group]
    return len(groups) == len(set(groups))


def value(plan: set[str]) -> int:
    return sum(by_id[i].value for i in plan)


def greedy() -> set[str]:
    plan: set[str] = set()
    for p in sorted(tiny.projects, key=lambda p: p.value / p.capex, reverse=True):
        if sum(by_id[i].capex for i in plan) + p.capex <= budget:
            plan.add(p.project_id)
    return plan


def brute_force() -> tuple[set[str], int]:
    checked, best = 0, None
    for k in range(len(by_id) + 1):
        for combo in combinations(by_id, k):
            checked += 1
            plan = set(combo)
            if allowed(plan) and (best is None or value(plan) > value(best)):
                best = plan
    return best, checked


if __name__ == "__main__":
    g = greedy()
    print("greedy", sorted(g), f"value ${value(g):,}k", "allowed" if allowed(g) else "breaks a rule")
    best, checked = brute_force()
    print("best  ", sorted(best), f"value ${value(best):,}k", f"cost ${sum(by_id[i].capex for i in best):,}k")
    print("plans checked:", checked)
