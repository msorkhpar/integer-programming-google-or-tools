from __future__ import annotations


def allowed_years(item: dict, years: list[int]) -> list[int]:
    """The plan years an item may be installed in: inside its release-deadline window."""
    return [t for t in years if item["release"] <= t <= item["deadline"]]


def precheck(items: dict, budget: dict, engineers: dict, dept_minimum: dict) -> list[tuple[str, str]]:
    """Every (check, subject) that proves the equipment program can have no plan, sorted."""
    # TODO: the five checks. Each must fire only when no plan can exist.
    return []


if __name__ == "__main__":
    items = {"MRI-2": {"dept": "radiology", "cost": 900, "release": 2027, "deadline": 2028, "required": True,
                       "engineer_days": 30, "excludes": None}}
    print(precheck(items, {2027: 800, 2028: 1000}, {2027: 40, 2028: 40}, {"radiology": 500}))
