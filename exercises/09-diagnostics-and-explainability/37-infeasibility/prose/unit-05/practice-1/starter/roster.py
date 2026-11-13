from __future__ import annotations

from ortools.sat.python import cp_model


def named_conflict(nurses: list[str], need: dict, max_shifts: dict, days_off: list) -> list[str] | None:
    """The roster rules CP-SAT names as clashing (sorted), or None if a roster exists."""
    # TODO: guard each rule with its own flag, assume every flag, solve with one worker,
    # and turn the indices the solver names back into rule names.
    return None


if __name__ == "__main__":
    print(named_conflict(["Ana", "Ben"], {1: 3}, {"Ana": 5, "Ben": 5}, []))
