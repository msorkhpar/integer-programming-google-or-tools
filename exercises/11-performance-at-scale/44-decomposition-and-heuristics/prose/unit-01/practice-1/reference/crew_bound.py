from __future__ import annotations


def crew_bound(builds: dict, hours: dict[int, int], prices: dict[int, float]) -> tuple[float, dict[str, int]]:
    """L(mu) for the crew rows priced at `prices`, and the relaxed plan that reaches it."""
    bound = sum(prices[y] * hours[y] for y in hours)
    plan = {}
    for name, build in builds.items():
        best_year, best = None, 0.0
        for t, v in build["value"].items():
            worth = v - sum(prices[t + k] * h for k, h in enumerate(build["hours"]))
            if (best_year is None and build["must"]) or worth > best:
                best_year, best = t, worth
        if best_year is not None:
            plan[name] = best_year
            bound += best
    return bound, plan


if __name__ == "__main__":
    builds = {"north ring": {"value": {2027: 50, 2028: 44}, "hours": [30, 10], "must": False}}
    print(crew_bound(builds, {2027: 40, 2028: 40}, {2027: 0.5, 2028: 0.5}))
