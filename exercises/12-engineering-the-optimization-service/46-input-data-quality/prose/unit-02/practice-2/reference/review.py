from __future__ import annotations

Finding = tuple[str, str, str]                  # (severity, rule, subject)


def starts(job: dict, horizon: list[int]) -> list[int]:
    """The start years in the job's window whose whole work falls inside the horizon."""
    return [t for t in range(job["earliest"], job["latest"] + 1)
            if t >= horizon[0] and t + len(job["cost"]) - 1 <= horizon[-1]]


def cycles(snapshot: dict) -> list[Finding]:
    after = {j["id"]: j["after"] for j in snapshot["jobs"]}
    found = set()
    for first in after:
        seen, jid = [], first
        while jid is not None and jid not in seen:
            seen.append(jid)
            jid = after[jid]
        if jid is not None:
            found.add(("error", "prerequisite-cycle", "+".join(sorted(seen[seen.index(jid):]))))
    return sorted(found)


def needed(snapshot: dict) -> set[str]:
    """Jobs every plan must do: the required ones and, through `after`, all their prerequisites."""
    by_id = {j["id"]: j for j in snapshot["jobs"]}
    need, todo = set(), [j["id"] for j in snapshot["jobs"] if j["required"]]
    while todo:
        jid = todo.pop()
        if jid not in need:
            need.add(jid)
            if by_id[jid]["after"] is not None:
                todo.append(by_id[jid]["after"])
    return need


def too_late(snapshot: dict) -> list[Finding]:
    by_id = {j["id"]: j for j in snapshot["jobs"]}
    need = needed(snapshot)
    found = []
    for job in snapshot["jobs"]:
        if job["after"] is None:
            continue
        mine, theirs = starts(job, snapshot["horizon"]), starts(by_id[job["after"]], snapshot["horizon"])
        if not any(s + job["lag"] <= t for s in theirs for t in mine):
            found.append(("error" if job["id"] in need else "warning", "prerequisite-too-late", job["id"]))
    return found


def no_start(snapshot: dict) -> list[Finding]:
    return [("error", "no-start-in-horizon", j["id"]) for j in snapshot["jobs"]
            if j["required"] and not starts(j, snapshot["horizon"])]


def over_budget(snapshot: dict) -> list[Finding]:
    by_id = {j["id"]: j for j in snapshot["jobs"]}
    need = needed(snapshot)
    if sum(sum(by_id[jid]["cost"]) for jid in need) > sum(snapshot["budgets"].values()):
        return [("error", "required-over-budget", "plan")]
    return []


def drift(snapshot: dict, previous: dict | None, factor: float = 3.0) -> list[Finding]:
    if previous is None:
        return []
    found = []
    for year, amount in snapshot["budgets"].items():
        old = previous["budgets"].get(year)
        if old and (amount > factor * old or amount * factor < old):
            found.append(("warning", "budget-drift", str(year)))
    return found


def review(snapshot: dict, previous: dict | None = None) -> list[Finding]:
    """Every finding of every rule, sorted: errors first."""
    return sorted(cycles(snapshot) + too_late(snapshot) + no_start(snapshot) + over_budget(snapshot)
                  + drift(snapshot, previous))


def rejected(findings: list[Finding]) -> bool:
    return any(severity == "error" for severity, _, _ in findings)


if __name__ == "__main__":
    snapshot = {"horizon": [2027, 2028], "budgets": {2027: 500, 2028: 500},
                "jobs": [{"id": "M1", "cost": [900], "earliest": 2027, "latest": 2028, "required": True,
                          "after": None, "lag": 0}]}
    print(review(snapshot))
