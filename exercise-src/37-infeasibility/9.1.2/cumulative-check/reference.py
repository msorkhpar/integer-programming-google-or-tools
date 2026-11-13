from __future__ import annotations


def cumulative_check(items: dict, budget: dict) -> list[tuple[int, int, int]]:
    """(year, must have been paid by then, money available by then) for every year that falls short."""
    short = []
    available = 0
    for year in sorted(budget):
        available += budget[year]
        due = sum(item["cost"] for item in items.values() if item["required"] and item["deadline"] <= year)
        if due > available:
            short.append((year, due, available))
    return short


if __name__ == "__main__":
    items = {"pump-A": {"cost": 600, "deadline": 2027, "required": True},
             "pump-B": {"cost": 700, "deadline": 2028, "required": True}}
    print(cumulative_check(items, {2027: 500, 2028: 500}))
