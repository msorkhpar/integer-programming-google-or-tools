from __future__ import annotations

from collections import Counter


def required(snapshot: dict) -> set[str]:
    """Jobs every plan must do: the required ones and, through `after`, all their prerequisites."""
    # TODO: the required jobs, then their prerequisites, and theirs, until none is new.
    return set()


def cross_checks(snapshot: dict) -> list[tuple[str, str]]:
    """(rule, subject) for each cross-job problem that proves no plan exists, sorted."""
    # TODO: write the two rules from the statement, using required().
    return [("not-checked", "")]


if __name__ == "__main__":
    jobs = [{"id": "T1", "crew": "track", "crew_weeks": 4, "required": True, "after": None, "exclusive": "G1"},
            {"id": "T2", "crew": "track", "crew_weeks": 3, "required": True, "after": None, "exclusive": "G1"}]
    print(cross_checks({"crews": {"track": 10}, "jobs": jobs}))
