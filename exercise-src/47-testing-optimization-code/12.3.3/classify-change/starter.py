"""Say what kind of change separates a crew-roster result from its golden record.

A record is a dict:
    "input":  the content hash of the data the roster was solved from
    "status": the solver's termination, e.g. "OPTIMAL"
    "cost":   the roster's cost in dollars; the model minimizes it
    "assign": {job: crew}
"""

from __future__ import annotations

COST_TOLERANCE = 1.0   # dollars


def classify(expected: dict, actual: dict) -> str:
    """One of "input", "status", "better", "worse", "tie" or "same"."""
    # TODO: check the causes in the right order.
    return "same"

if __name__ == "__main__":
    golden = {"input": "9f2c", "status": "OPTIMAL", "cost": 980.0, "assign": {"j1": "red"}}
    print(classify(golden, {**golden, "cost": 940.0}))
