from __future__ import annotations


def cumulative_check(items: dict, budget: dict) -> list[tuple[int, int, int]]:
    """(year, must have been paid by then, money available by then) for every year that falls short."""
    # TODO: year by year, what must have been paid by then against what has been available by then.
    return []


if __name__ == "__main__":
    items = {"pump-A": {"cost": 600, "deadline": 2027, "required": True},
             "pump-B": {"cost": 700, "deadline": 2028, "required": True}}
    print(cumulative_check(items, {2027: 500, 2028: 500}))
