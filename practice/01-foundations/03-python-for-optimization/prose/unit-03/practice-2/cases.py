from __future__ import annotations

# The outage team's validator. It is finished and tested; do not change it.
CREWS = {"line-1", "line-2", "veg-1"}
RULES = ("hours-not-a-number", "negative-hours", "unknown-crew", "week-out-of-range", "end-before-start",
         "priority-out-of-range")


def check_request(row: dict[str, str]) -> list[str]:
    """Every rule an outage request breaks, by name (an empty list for a valid request)."""
    problems = []
    try:
        hours = float(row["hours"])
    except ValueError:
        problems.append("hours-not-a-number")
    else:
        if hours < 0:
            problems.append("negative-hours")
    if row["crew"] not in CREWS:
        problems.append("unknown-crew")
    start, end = int(row["start_week"]), int(row["end_week"])
    if not (1 <= start <= 52 and 1 <= end <= 52):
        problems.append("week-out-of-range")
    if end < start:
        problems.append("end-before-start")
    if row["priority"] not in {"1", "2", "3", "4", "5"}:
        problems.append("priority-out-of-range")
    return problems


#: A valid request. Build each case from a copy of it.
BASE = {"feeder": "F-12", "crew": "line-1", "start_week": "10", "end_week": "12", "hours": "36", "priority": "2"}


# Your table: six (row, rule) pairs, one per rule in RULES.
CASES: list[tuple[dict[str, str], str]] = [
    # TODO: (a request that breaks this rule and no other, "the-rule's-name"), one per rule
]

if __name__ == "__main__":
    for row, rule in CASES:
        print(rule, "->", check_request(row))
