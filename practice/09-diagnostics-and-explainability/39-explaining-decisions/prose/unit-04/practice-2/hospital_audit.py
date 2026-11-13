from __future__ import annotations


def audit_failures(plan: dict[str, int], items: dict[str, dict], budget: dict[int, int],
                   groups: dict[str, list[str]]) -> list[str]:
    """Check a purchase plan {item: year} against the rules from the data alone; list what fails, sorted."""
    # TODO: one check per rule, each reading only the data and the plan.
    return []

if __name__ == "__main__":
    items = {"sterilizer": {"years": [2027], "cost": 400, "mandatory": True}}
    print(audit_failures({}, items, {2027: 500}, {}))
