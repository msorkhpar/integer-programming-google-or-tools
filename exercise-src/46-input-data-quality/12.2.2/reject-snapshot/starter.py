from __future__ import annotations

Finding = tuple[str, str, str]                  # (severity, rule, subject)


def starts(job: dict, horizon: list[int]) -> list[int]:
    """The start years in the job's window whose whole work falls inside the horizon."""
    # TODO
    return []


def cycles(snapshot: dict) -> list[Finding]:
    # TODO: one finding per cycle of prerequisites, its jobs sorted and joined with "+".
    return []


def too_late(snapshot: dict) -> list[Finding]:
    # TODO: a job whose prerequisite cannot start early enough for any of its own start years.
    return []


def no_start(snapshot: dict) -> list[Finding]:
    # TODO: a required job with no start year.
    return []


def over_budget(snapshot: dict) -> list[Finding]:
    # TODO: what every plan must pay for, against all the budgets together.
    return []


def drift(snapshot: dict, previous: dict | None, factor: float = 3.0) -> list[Finding]:
    # TODO: a year's budget more than `factor` times larger or smaller than in `previous`.
    return []


def review(snapshot: dict, previous: dict | None = None) -> list[Finding]:
    """Every finding of every rule, sorted: errors first."""
    # TODO: run every rule.
    return [("?", "not reviewed", "")]


def rejected(findings: list[Finding]) -> bool:
    return any(severity == "error" for severity, _, _ in findings)


if __name__ == "__main__":
    snapshot = {"horizon": [2027, 2028], "budgets": {2027: 500, 2028: 500},
                "jobs": [{"id": "M1", "cost": [900], "earliest": 2027, "latest": 2028, "required": True,
                          "after": None, "lag": 0}]}
    print(review(snapshot))
