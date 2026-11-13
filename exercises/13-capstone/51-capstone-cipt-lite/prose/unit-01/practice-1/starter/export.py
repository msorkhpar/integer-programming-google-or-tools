from __future__ import annotations

PROGRAMS = ("lines", "poles")
REGIONS = ("North", "South")

Finding = tuple[str, str, str]                  # (severity, rule, subject)


def whole(text: str) -> int | None:
    """The cell as a whole number, or None if it is not one."""
    try:
        return int(text)
    except ValueError:
        return None


def read_rows(export: dict) -> tuple[dict | None, list[Finding]]:
    """The practice snapshot built from the export's text cells, and every cell problem.

    Returns (None, findings) when there is any problem, but only after reading every row.
    """
    # TODO: read the budget rows, then every project row; keep every problem as a finding.
    return None, []


def cross_rules(snap: dict) -> list[Finding]:
    """The rules that look across projects; they assume every cell is clean."""
    # TODO: parent-cycle, parent-too-late, must-spend-over-budget.
    return []


def review(export: dict) -> tuple[dict | None, list[Finding]]:
    """Cells first; the cross-project rules only on a snapshot whose cells are all clean."""
    snap, found = read_rows(export)
    if snap is None:
        return None, sorted(found)
    found = cross_rules(snap)
    return (None if rejected(found) else snap), sorted(found)


def rejected(findings: list[Finding]) -> bool:
    return any(severity == "error" for severity, _, _ in findings)


if __name__ == "__main__":
    export = {"years": [2027, 2028], "rate": "0.05", "budgets": [{"year": "2027", "amount": "100"},
                                                                 {"year": "2028", "amount": "1oo"}],
              "projects": [{"id": "J1", "program": "lines", "region": "North", "cost": "50", "earliest": "2027",
                            "latest": "2028", "must": "1", "parent": "", "lag": "0", "group": "", "crews": "1"}]}
    print(review(export))
