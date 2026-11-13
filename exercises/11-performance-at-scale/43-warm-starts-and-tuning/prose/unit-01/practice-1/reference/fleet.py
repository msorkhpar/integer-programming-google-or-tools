from __future__ import annotations


def carry_forward(old_plan: dict[str, int], windows: dict[str, list[int]], first_year: int) -> dict[tuple[str, int], float]:
    """Last cycle's plan as a complete start for this cycle's variables x[(bus, year)]."""
    start = {}
    for bus, years in windows.items():
        planned = old_plan.get(bus)
        for year in years:
            start[bus, year] = 1.0 if planned == year and planned > first_year else 0.0
    return start


def committed(old_plan: dict[str, int], first_year: int) -> set[str]:
    """The buses last cycle's plan replaces in the year that has now begun: no longer decisions."""
    return {bus for bus, year in old_plan.items() if year == first_year}


if __name__ == "__main__":
    old = {"B1": 2027, "B2": 2029, "B3": 2028}
    windows = {"B2": [2028, 2029, 2030], "B3": [2029, 2030], "B9": [2028, 2029]}
    print(committed(old, 2027))
    print(carry_forward(old, windows, 2027))
