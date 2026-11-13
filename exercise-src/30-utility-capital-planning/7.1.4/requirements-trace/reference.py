from __future__ import annotations

STATES = ("MET", "FAILED", "UNTESTED")


def trace(requirements: list[dict], checks: list[dict]) -> dict[str, str]:
    """Requirement id -> MET, FAILED or UNTESTED, from the checks that cover it."""
    status = {}
    for r in requirements:
        results = [c["passed"] for c in checks if r["id"] in c["covers"]]
        if not results:
            status[r["id"]] = "UNTESTED"
        elif all(results):
            status[r["id"]] = "MET"
        else:
            status[r["id"]] = "FAILED"
    return status


def by_stakeholder(requirements: list[dict], status: dict[str, str]) -> dict[str, dict[str, int]]:
    """Stakeholder -> how many of their requirements are in each state, zeros included."""
    table: dict[str, dict[str, int]] = {}
    for r in requirements:
        row = table.setdefault(r["stakeholder"], {s: 0 for s in STATES})
        row[status[r["id"]]] += 1
    return table


if __name__ == "__main__":
    reqs = [{"id": "Q1", "stakeholder": "finance", "text": "spend within each year"}]
    checks = [{"name": "yearly_spend", "covers": ["Q1"], "passed": True}]
    status = trace(reqs, checks)
    print(status, by_stakeholder(reqs, status))
