from __future__ import annotations


def allowed_years(item: dict, years: list[int]) -> list[int]:
    """The plan years an item may be installed in: inside its release-deadline window."""
    return [t for t in years if item["release"] <= t <= item["deadline"]]


def precheck(items: dict, budget: dict, engineers: dict, dept_minimum: dict) -> list[tuple[str, str]]:
    """Every (check, subject) that proves the equipment program can have no plan, sorted."""
    years = sorted(budget)
    found = []
    for name, item in items.items():
        if not item["required"]:
            continue
        options = allowed_years(item, years)
        if not options:
            found.append(("window", name))
            continue
        if all(item["cost"] > budget[t] for t in options):
            found.append(("budget", name))
        if all(item["engineer_days"] > engineers[t] for t in options):
            found.append(("engineers", name))
    for name, item in items.items():
        other = item["excludes"]
        if other and item["required"] and items[other]["required"]:
            found.append(("exclusion", "|".join(sorted((name, other)))))
    for dept, minimum in dept_minimum.items():
        supply = sum(item["cost"] for item in items.values() if item["dept"] == dept)
        if supply < minimum:
            found.append(("minimum", dept))
    return sorted(set(found))


if __name__ == "__main__":
    items = {"MRI-2": {"dept": "radiology", "cost": 900, "release": 2027, "deadline": 2028, "required": True,
                       "engineer_days": 30, "excludes": None}}
    print(precheck(items, {2027: 800, 2028: 1000}, {2027: 40, 2028: 40}, {"radiology": 500}))
