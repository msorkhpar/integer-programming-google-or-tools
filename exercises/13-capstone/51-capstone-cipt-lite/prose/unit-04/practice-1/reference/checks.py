from __future__ import annotations

Finding = tuple[str, str]                         # (rule, subject)


def starts(project: dict) -> list[int]:
    return list(range(project["earliest"], project["latest"] + 1))


def spend(project: dict, start: int) -> dict[int, int]:
    """What the project spends in each calendar year if it starts in `start`."""
    return {start + k: amount for k, amount in enumerate(project["cost"])}


def budgets(snapshot: dict, scenario: dict) -> dict[int, int]:
    return {y: scenario.get("budget", {}).get(y, snapshot["budget"][y]) for y in snapshot["years"]}


def crews(snapshot: dict, scenario: dict, program: str, year: int) -> int:
    return scenario.get("crews", {}).get(program, {}).get(year, snapshot["crews"][program][year])


def required(snapshot: dict, scenario: dict) -> dict[str, list[int]]:
    """Every project each plan must fund, with the start years left to it."""
    need = {pid: starts(p) for pid, p in snapshot["projects"].items()
            if p["must"] or pid in scenario.get("force_in", [])}
    for pid, year in scenario.get("fix_start", {}).items():
        need[pid] = [year]
    return need


def checks(snapshot: dict, scenario: dict) -> list[Finding]:
    projects, limit = snapshot["projects"], budgets(snapshot, scenario)
    need = required(snapshot, scenario)
    found = []
    for pid, years in sorted(need.items()):
        p = projects[pid]
        if pid in scenario.get("force_out", []) or not set(years) <= set(starts(p)):
            found.append(("no-start", pid))
            continue
        if not any(all(a <= limit[y] for y, a in spend(p, t).items()) for t in years):
            found.append(("alone-over-budget", pid))
        if not any(all(p["crews"] <= crews(snapshot, scenario, p["program"], y) for y in spend(p, t))
                   for t in years):
            found.append(("alone-over-crews", pid))
    for y in snapshot["years"]:
        least = sum(min(spend(projects[pid], t).get(y, 0) for t in years)
                    for pid, years in need.items() if set(years) <= set(starts(projects[pid])))
        if least > limit[y]:
            found.append(("required-over-budget", str(y)))
    groups: dict[str, int] = {}
    for pid in need:
        if projects[pid]["group"]:
            groups[projects[pid]["group"]] = groups.get(projects[pid]["group"], 0) + 1
    found += [("required-alternatives", g) for g, n in sorted(groups.items()) if n > 1]
    for region, floor in sorted(snapshot["floor"].items()):
        most = sum(sum(p["cost"]) for pid, p in projects.items()
                   if p["region"] == region and pid not in scenario.get("force_out", []))
        if most < floor:
            found.append(("floor-out-of-reach", region))
    return found


if __name__ == "__main__":
    snapshot = {"years": [2027], "budget": {2027: 100}, "crews": {"lines": {2027: 2}}, "floor": {},
                "projects": {"J1": {"program": "lines", "region": "North", "cost": [150], "earliest": 2027,
                                    "latest": 2027, "must": True, "group": None, "crews": 1}}}
    print(checks(snapshot, {"name": "lock"}))
