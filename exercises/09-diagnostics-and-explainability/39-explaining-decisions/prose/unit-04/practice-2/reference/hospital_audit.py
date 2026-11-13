from __future__ import annotations


def audit_failures(plan: dict[str, int], items: dict[str, dict], budget: dict[int, int],
                   groups: dict[str, list[str]]) -> list[str]:
    """Check a purchase plan {item: year} against the rules from the data alone; list what fails, sorted."""
    failures = []
    for name, year in plan.items():
        if year not in items[name]["years"]:
            failures.append(f"window {name}")
    for name, item in items.items():
        if item["mandatory"] and name not in plan:
            failures.append(f"mandatory {name}")
    for group, members in groups.items():
        if sum(1 for name in members if name in plan) > 1:
            failures.append(f"exclusive {group}")
    for year, limit in budget.items():
        spent = sum(items[name]["cost"] for name, y in plan.items() if y == year)
        if spent > limit:
            failures.append(f"budget {year}")
    return sorted(failures)


if __name__ == "__main__":
    items = {"sterilizer": {"years": [2027], "cost": 400, "mandatory": True}}
    print(audit_failures({}, items, {2027: 500}, {}))
