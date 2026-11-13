"""Compare a crew-roster result with its golden record.

A record is a dict:
    "status":   the solver's termination, e.g. "OPTIMAL"
    "cost":     the roster's cost in dollars (a float from the solver)
    "assign":   {job: crew}
    "overtime": {crew: overtime hours} (floats from the solver; a crew not listed has 0)
"""

from __future__ import annotations

TOLERANCE = {"cost": 1.0, "overtime": 0.01}   # $1 on cost; 0.01 hours (36 seconds) on overtime


def compare(expected: dict, actual: dict) -> list[str]:
    """One line per difference, in the order: status, cost, assignments, overtime."""
    if expected["status"] != actual["status"]:
        return [f"status: {expected['status']} -> {actual['status']}"]
    lines = []
    if abs(actual["cost"] - expected["cost"]) > TOLERANCE["cost"]:
        lines.append(f"cost: {expected['cost']:.2f} -> {actual['cost']:.2f}")
    was, now = expected["assign"], actual["assign"]
    for job in sorted(set(was) | set(now)):
        if was.get(job) != now.get(job):
            lines.append(f"assign: {job} {was.get(job, 'none')} -> {now.get(job, 'none')}")
    before, after = expected["overtime"], actual["overtime"]
    for crew in sorted(set(before) | set(after)):
        b, a = before.get(crew, 0.0), after.get(crew, 0.0)
        if abs(a - b) > TOLERANCE["overtime"]:
            lines.append(f"overtime {crew}: {b:.2f} -> {a:.2f}")
    return lines


if __name__ == "__main__":
    golden = {"status": "OPTIMAL", "cost": 1200.0, "assign": {"j1": "red"}, "overtime": {"red": 2.0}}
    print(compare(golden, {**golden, "cost": 1250.0}))
