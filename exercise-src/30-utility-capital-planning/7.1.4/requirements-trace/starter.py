from __future__ import annotations

STATES = ("MET", "FAILED", "UNTESTED")


def trace(requirements: list[dict], checks: list[dict]) -> dict[str, str]:
    """Requirement id -> MET, FAILED or UNTESTED, from the checks that cover it."""
    # TODO: look at the checks that cover each requirement. "MET" is a placeholder.
    return {r["id"]: "MET" for r in requirements}


def by_stakeholder(requirements: list[dict], status: dict[str, str]) -> dict[str, dict[str, int]]:
    """Stakeholder -> how many of their requirements are in each state, zeros included."""
    # TODO: count each stakeholder's requirements by state. The empty dict is a placeholder.
    return {}


if __name__ == "__main__":
    reqs = [{"id": "Q1", "stakeholder": "finance", "text": "spend within each year"}]
    checks = [{"name": "yearly_spend", "covers": ["Q1"], "passed": True}]
    status = trace(reqs, checks)
    print(status, by_stakeholder(reqs, status))
