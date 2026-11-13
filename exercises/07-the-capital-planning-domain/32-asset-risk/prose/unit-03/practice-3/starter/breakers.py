import math


def cumulative_hazard(t: float, beta: float, eta: float) -> float:
    return (t / eta) ** beta


def failures_by_year(ages: list[float], beta: float, eta: float, years: int) -> list[float]:
    """The fleet's expected failures in each of the next `years` years, coming year first."""
    # TODO: one number per year, summed over the breakers at the ages they will have that year.
    return [0.0] * years


def chance_of_none(age: float, beta: float, eta: float, years: int) -> float:
    """The chance a breaker working at `age` has no failure in the next `years` years."""
    # TODO
    return 0.0


if __name__ == "__main__":
    print(failures_by_year([10, 25, 40], 2.5, 35, 3), chance_of_none(25, 2.5, 35, 5))
