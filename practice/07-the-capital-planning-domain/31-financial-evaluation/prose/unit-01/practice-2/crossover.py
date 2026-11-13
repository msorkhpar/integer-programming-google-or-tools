from __future__ import annotations


def npv(rate: float, values: list[float]) -> float:
    """Value now of yearly amounts, the first one now (numpy-financial's convention)."""
    return sum(v / (1 + rate) ** t for t, v in enumerate(values))


def crossover_rate(a: list[float], b: list[float], low: float = 0.0, high: float = 1.0) -> float:
    """The rate in [low, high] at which options a and b have the same value."""
    # TODO: find the rate where npv(rate, a) == npv(rate, b).
    return -1.0


if __name__ == "__main__":
    print(crossover_rate([-600] + [100] * 10, [-600] + [220] * 4 + [0] * 6))
