from __future__ import annotations


def spend_by_year(snap: dict, plan: dict[str, int]) -> dict[int, int]:
    """What the plan spends in each year of the horizon, $k: cost[k] lands in year start + k."""
    # TODO
    return {y: 0 for y in snap["years"]}


def broken(snap: dict, plan: dict[str, int]) -> list[str]:
    """The names of every row the plan breaks, sorted, read from the data alone."""
    # TODO: window, must, alt, after, budget, region, crews and floor.
    return ["not checked"]


if __name__ == "__main__":
    snap = {"years": [2027, 2028], "rate": 0.05, "budget": {2027: 100, 2028: 100},
            "region_budget": {"North": {2027: 100, 2028: 100}}, "crews": {"lines": {2027: 1, 2028: 1}},
            "floor": {"North": 0},
            "projects": {"J1": {"program": "lines", "region": "North", "cost": [80, 40], "earliest": 2027,
                                "latest": 2027, "must": True, "parent": None, "lag": 0, "group": None,
                                "crews": 1, "npv": {2027: 30}}}}
    print(broken(snap, {"J1": 2027}), broken(snap, {}))
