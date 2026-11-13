from __future__ import annotations


def spend_by_year(snap: dict, plan: dict[str, int]) -> dict[int, int]:
    """What the plan spends in each year of the horizon, $k: cost[k] lands in year start + k."""
    out = {y: 0 for y in snap["years"]}
    for pid, start in plan.items():
        for k, amount in enumerate(snap["projects"][pid]["cost"]):
            if start + k in out:
                out[start + k] += amount
    return out


def broken(snap: dict, plan: dict[str, int]) -> list[str]:
    """The names of every row the plan breaks, sorted, read from the data alone."""
    projects, years = snap["projects"], snap["years"]
    out = []
    for pid, start in plan.items():
        p = projects[pid]
        if not p["earliest"] <= start <= p["latest"]:
            out.append(f"window_{pid}")
    out += [f"must_{pid}" for pid, p in projects.items() if p["must"] and pid not in plan]
    groups: dict[str, int] = {}
    for pid in plan:
        group = projects[pid]["group"]
        if group is not None:
            groups[group] = groups.get(group, 0) + 1
    out += [f"alt_{g}" for g, n in groups.items() if n > 1]
    for pid, start in plan.items():
        parent, lag = projects[pid]["parent"], projects[pid]["lag"]
        if parent is not None and (parent not in plan or plan[parent] + lag > start):
            out.append(f"after_{pid}_{start}")
    total = spend_by_year(snap, plan)
    out += [f"budget_{y}" for y in years if total[y] > snap["budget"][y]]
    for region, limits in snap["region_budget"].items():
        mine = spend_by_year(snap, {i: t for i, t in plan.items() if projects[i]["region"] == region})
        out += [f"region_{region}_{y}" for y in years if mine[y] > limits[y]]
    for program, limits in snap["crews"].items():
        use = {y: 0 for y in years}
        for pid, start in plan.items():
            p = projects[pid]
            if p["program"] == program:
                for y in range(start, start + len(p["cost"])):
                    if y in use:
                        use[y] += p["crews"]
        out += [f"crews_{program}_{y}" for y in years if use[y] > limits[y]]
    for region, floor in snap["floor"].items():
        funded = sum(sum(projects[i]["cost"]) for i in plan if projects[i]["region"] == region)
        if funded < floor:
            out.append(f"floor_{region}")
    return sorted(out)


if __name__ == "__main__":
    snap = {"years": [2027, 2028], "rate": 0.05, "budget": {2027: 100, 2028: 100},
            "region_budget": {"North": {2027: 100, 2028: 100}}, "crews": {"lines": {2027: 1, 2028: 1}},
            "floor": {"North": 0},
            "projects": {"J1": {"program": "lines", "region": "North", "cost": [80, 40], "earliest": 2027,
                                "latest": 2027, "must": True, "parent": None, "lag": 0, "group": None,
                                "crews": 1, "npv": {2027: 30}}}}
    print(broken(snap, {"J1": 2027}), broken(snap, {}))
