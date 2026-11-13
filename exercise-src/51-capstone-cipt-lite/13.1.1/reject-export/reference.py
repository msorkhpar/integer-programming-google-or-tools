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

    Returns (None, findings) as soon as there is any problem, but only after reading every row.
    """
    years = export["years"]
    found: list[Finding] = []
    budget = {}
    for row in export["budgets"]:
        year, amount = whole(row["year"]), whole(row["amount"])
        if year is None or amount is None or amount < 0:
            found.append(("error", "bad-budget", row["year"]))
        else:
            budget[year] = amount
    for y in years:
        if y not in budget and ("error", "bad-budget", str(y)) not in found:
            found.append(("error", "missing-budget", str(y)))

    projects, ids = {}, [row["id"] for row in export["projects"]]
    for row in export["projects"]:
        pid = row["id"]
        if ids.count(pid) > 1 and pid in projects:
            found.append(("error", "duplicate-id", pid))
            continue
        cost = [whole(part) for part in row["cost"].split(";")]
        if any(c is None or c <= 0 for c in cost):
            found.append(("error", "not-a-number", f"{pid}.cost"))
        numbers = {}
        for column in ("earliest", "latest", "lag", "crews"):
            numbers[column] = whole(row[column])
            if numbers[column] is None:
                found.append(("error", "not-a-number", f"{pid}.{column}"))
        if row["program"] not in PROGRAMS:
            found.append(("error", "unknown-code", f"{pid}.program"))
        if row["region"] not in REGIONS:
            found.append(("error", "unknown-code", f"{pid}.region"))
        if row["must"] not in ("0", "1"):
            found.append(("error", "unknown-code", f"{pid}.must"))
        first, last = numbers["earliest"], numbers["latest"]
        if first is not None and last is not None and not (
                years[0] <= first <= last and last + len(cost) - 1 <= years[-1]):
            found.append(("error", "empty-window", pid))
        projects[pid] = {"program": row["program"], "region": row["region"], "cost": cost,
                         "earliest": first, "latest": last, "must": row["must"] == "1",
                         "parent": row["parent"] or None, "lag": numbers["lag"],
                         "group": row["group"] or None, "crews": numbers["crews"]}
    for pid, p in projects.items():
        if p["parent"] is not None and p["parent"] not in projects:
            found.append(("error", "unknown-parent", pid))
    if found:
        return None, found
    return {"years": list(years), "rate": float(export["rate"]), "budget": budget, "projects": projects}, []


def cross_rules(snap: dict) -> list[Finding]:
    """The rules that look across projects; they assume every cell is clean."""
    projects, found = snap["projects"], []
    seen_cycles = set()
    for start in sorted(projects):
        path, pid = [], start
        while pid is not None and pid not in path:
            path.append(pid)
            pid = projects[pid]["parent"]
        if pid is not None:
            loop = frozenset(path[path.index(pid):])
            if loop not in seen_cycles:
                seen_cycles.add(loop)
                found.append(("error", "parent-cycle", "+".join(sorted(loop))))
    for pid, p in sorted(projects.items()):
        if p["parent"] is None:
            continue
        parent = projects[p["parent"]]
        if parent["earliest"] + p["lag"] > p["latest"]:
            found.append(("error" if p["must"] else "warning", "parent-too-late", pid))
    for y in snap["years"]:
        least = 0
        for p in projects.values():
            if p["must"]:
                least += min(p["cost"][y - t] if 0 <= y - t < len(p["cost"]) else 0
                             for t in range(p["earliest"], p["latest"] + 1))
        if least > snap["budget"][y]:
            found.append(("error", "must-spend-over-budget", str(y)))
    return found


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
