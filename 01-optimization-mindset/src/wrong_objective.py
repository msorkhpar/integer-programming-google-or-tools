"""Rank plans by how many projects they fund instead of by NPV, and see what drops out."""

from itertools import combinations

from greedy_vs_best import allowed, by_id, value


def most_projects() -> set[str]:
    best = None
    for k in range(len(by_id) + 1):
        for combo in combinations(by_id, k):
            plan = set(combo)
            if allowed(plan) and (best is None or (len(plan), value(plan)) > (len(best), value(best))):
                best = plan
    return best


if __name__ == "__main__":
    plan = most_projects()
    print("most projects:", sorted(plan), f"count {len(plan)}", f"value ${value(plan):,}k")
