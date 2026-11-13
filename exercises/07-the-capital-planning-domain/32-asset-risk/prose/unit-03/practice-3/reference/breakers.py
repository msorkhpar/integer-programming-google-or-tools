import math


def cumulative_hazard(t: float, beta: float, eta: float) -> float:
    return (t / eta) ** beta


def failures_by_year(ages: list[float], beta: float, eta: float, years: int) -> list[float]:
    """The fleet's expected failures in each of the next `years` years, coming year first."""
    out = []
    for k in range(years):
        out.append(sum(cumulative_hazard(a + k + 1, beta, eta) - cumulative_hazard(a + k, beta, eta) for a in ages))
    return out


def chance_of_none(age: float, beta: float, eta: float, years: int) -> float:
    """The chance a breaker working at `age` has no failure in the next `years` years."""
    return math.exp(-(cumulative_hazard(age + years, beta, eta) - cumulative_hazard(age, beta, eta)))


if __name__ == "__main__":
    print(failures_by_year([10, 25, 40], 2.5, 35, 3), chance_of_none(25, 2.5, 35, 5))
