import math


def years_until(age: float, q: float, beta: float, eta: float) -> float:
    """Years from today until the chance a gearbox working at `age` has failed reaches q."""
    return eta * ((age / eta) ** beta - math.log(1 - q)) ** (1 / beta) - age


if __name__ == "__main__":
    print(years_until(12, 0.1, 2.8, 25))
