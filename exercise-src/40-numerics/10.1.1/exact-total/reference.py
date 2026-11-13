from __future__ import annotations


def to_cents(amount: float) -> int:
    """The amount, in dollars with cents, as an integer number of cents."""
    return round(amount * 100)


def fits(amounts: list[float], budget: float) -> bool:
    """True if the amounts add up to at most the budget, exact to the cent."""
    return sum(to_cents(a) for a in amounts) <= to_cents(budget)


if __name__ == "__main__":
    print(fits([0.1, 0.2], 0.3), fits([0.1, 0.2, 0.05], 0.3))
