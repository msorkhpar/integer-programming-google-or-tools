from __future__ import annotations


def quarters(start: str) -> int:
    """'2028-Q3' as a count of quarters, so that later starts are larger and a year has four."""
    year, quarter = start.split("-Q")
    return 4 * int(year) + int(quarter) - 1


def diff_scenarios(a: dict, b: dict) -> dict:
    """What changed from scenario a's plan to scenario b's: adds, drops and timing shifts in quarters."""
    before = {row["id"]: row["start"] for row in a["plan"]}
    after = {row["id"]: row["start"] for row in b["plan"]}
    adds, drops, shifts = [], [], []
    for pid in sorted(before.keys() | after.keys()):
        if pid not in before:
            adds.append(pid)
        elif pid not in after:
            drops.append(pid)
        elif before[pid] != after[pid]:
            shifts.append({"id": pid, "from": before[pid], "to": after[pid],
                           "quarters": quarters(after[pid]) - quarters(before[pid])})
    return {"adds": adds, "drops": drops, "shifts": shifts}


if __name__ == "__main__":
    spring = {"name": "spring", "plan": [{"id": "PR-11", "start": "2028-Q1"}]}
    summer = {"name": "summer", "plan": [{"id": "PR-11", "start": "2028-Q3"}]}
    print(diff_scenarios(spring, summer))
