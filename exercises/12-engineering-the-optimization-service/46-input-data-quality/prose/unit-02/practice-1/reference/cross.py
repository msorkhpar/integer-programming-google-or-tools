from __future__ import annotations

from collections import Counter


def required(snapshot: dict) -> set[str]:
    """Jobs every plan must do: the required ones and, through `after`, all their prerequisites."""
    by_id = {j["id"]: j for j in snapshot["jobs"]}
    need, todo = set(), [j["id"] for j in snapshot["jobs"] if j["required"]]
    while todo:
        jid = todo.pop()
        if jid not in need:
            need.add(jid)
            if by_id[jid]["after"]:
                todo.append(by_id[jid]["after"])
    return need


def cross_checks(snapshot: dict) -> list[tuple[str, str]]:
    """(rule, subject) for each cross-job problem that proves no plan exists, sorted."""
    by_id = {j["id"]: j for j in snapshot["jobs"]}
    need = required(snapshot)
    found = []
    taken = Counter(by_id[jid]["exclusive"] for jid in need if by_id[jid]["exclusive"])
    found += [("exclusive-required", group) for group, n in taken.items() if n > 1]
    for crew, supply in snapshot["crews"].items():
        demand = sum(by_id[jid]["crew_weeks"] for jid in need if by_id[jid]["crew"] == crew)
        if demand > supply:
            found.append(("crew-short", crew))
    return sorted(found)


if __name__ == "__main__":
    jobs = [{"id": "T1", "crew": "track", "crew_weeks": 4, "required": True, "after": None, "exclusive": "G1"},
            {"id": "T2", "crew": "track", "crew_weeks": 3, "required": True, "after": None, "exclusive": "G1"}]
    print(cross_checks({"crews": {"track": 10}, "jobs": jobs}))
