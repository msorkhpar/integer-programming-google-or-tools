from __future__ import annotations


def carry_forward(old_plan: dict[str, int], windows: dict[str, list[int]], first_year: int) -> dict[tuple[str, int], float]:
    """Last cycle's plan as a complete start for this cycle's variables x[(bus, year)]."""
    # TODO: one value for every (bus, year) variable of this cycle; write the rule down first.
    return {}


def committed(old_plan: dict[str, int], first_year: int) -> set[str]:
    """The buses last cycle's plan replaces in the year that has now begun: no longer decisions."""
    # TODO: the buses whose planned year is the year that has begun.
    return set()


if __name__ == "__main__":
    old = {"B1": 2027, "B2": 2029, "B3": 2028}
    windows = {"B2": [2028, 2029, 2030], "B3": [2029, 2030], "B9": [2028, 2029]}
    print(committed(old, 2027))
    print(carry_forward(old, windows, 2027))
