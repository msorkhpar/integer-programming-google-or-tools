from __future__ import annotations


def to_plan_date(values_at_start: dict[int, float], rate: float, plan_year: int) -> dict[int, float]:
    """{start year: value at the start of plan_year}, from values each taken at its own start year."""
    moved = {}
    for start, value in values_at_start.items():
        moved[start] = value / (1 + rate) ** (start - plan_year)
    return moved


if __name__ == "__main__":
    print(to_plan_date({2027: 500, 2028: 500, 2029: 500}, 0.06, 2027))
