import math


def trigger_age(rate: float, beta: float, eta: float) -> float | None:
    """Age (years) at which the failure rate of relays still working reaches `rate`; None if it never rises."""
    # TODO: solve h(t) = rate for t, and return None for the shapes whose rate never rises.
    return 0.0


if __name__ == "__main__":
    print(trigger_age(0.05, 3.0, 30.0))
