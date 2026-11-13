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


def changed(field: str, value: str) -> dict[str, str]:
    row = dict(BASE)
    row[field] = value
    return row


# Your table: six (row, rule) pairs, one per rule in RULES.
CASES: list[tuple[dict[str, str], str]] = [
    (changed("hours", "8,5"), "hours-not-a-number"),
    (changed("hours", "-4"), "negative-hours"),
    (changed("crew", "line-9"), "unknown-crew"),
    (changed("end_week", "53"), "week-out-of-range"),
    (changed("end_week", "9"), "end-before-start"),
    (changed("priority", "7"), "priority-out-of-range"),
]


if __name__ == "__main__":
    for row, rule in CASES:
        print(rule, "->", check_request(row))
