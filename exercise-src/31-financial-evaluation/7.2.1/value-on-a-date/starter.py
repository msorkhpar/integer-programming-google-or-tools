from __future__ import annotations


def value_on(flows: dict[int, float], rate: float, on_year: int) -> float:
    """The value at the start of `on_year` of {calendar year: amount}, each paid at the start of its year."""
    # TODO: discount (or compound) every amount to the start of on_year and add them up.
    return 0.0


if __name__ == "__main__":
    print(value_on({2026: -500, 2027: 200, 2028: 200, 2029: 200}, 0.06, 2026))
