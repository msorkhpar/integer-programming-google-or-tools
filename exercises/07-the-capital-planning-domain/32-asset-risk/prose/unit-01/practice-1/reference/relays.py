import math


def trigger_age(rate: float, beta: float, eta: float) -> float | None:
    """Age (years) at which the failure rate of relays still working reaches `rate`; None if it never rises."""
    if beta <= 1:
        return None
    return eta * (rate * eta / beta) ** (1 / (beta - 1))


if __name__ == "__main__":
    print(trigger_age(0.05, 3.0, 30.0))
