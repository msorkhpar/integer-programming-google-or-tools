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
    # TODO: status first, then each field with its tolerance.
    return []

if __name__ == "__main__":
    golden = {"status": "OPTIMAL", "cost": 1200.0, "assign": {"j1": "red"}, "overtime": {"red": 2.0}}
    print(compare(golden, {**golden, "cost": 1250.0}))
