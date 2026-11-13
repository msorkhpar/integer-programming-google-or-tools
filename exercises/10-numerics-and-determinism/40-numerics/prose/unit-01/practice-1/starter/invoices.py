from __future__ import annotations


def to_cents(amount: float) -> int:
    """The amount, in dollars with cents, as an integer number of cents."""
    # TODO: turn the float into the whole number of cents it stands for.
    return 0


def fits(amounts: list[float], budget: float) -> bool:
    """True if the amounts add up to at most the budget, exact to the cent."""
    # TODO: compare whole cents, so that float rounding cannot change the answer.
    return False


if __name__ == "__main__":
    print(fits([0.1, 0.2], 0.3), fits([0.1, 0.2, 0.05], 0.3))
