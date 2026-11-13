import math


def cumulative(t: float, beta: float, eta: float) -> float:
    """Weibull probability that an asset has failed by age t."""
    return 1 - math.exp(-((t / eta) ** beta))


def pof_within(age: float, years: float, beta: float, eta: float) -> float:
    """Probability of failing in the next `years` years, given the asset works at `age`."""
    survived = 1 - cumulative(age, beta, eta)
    return (cumulative(age + years, beta, eta) - cumulative(age, beta, eta)) / survived


if __name__ == "__main__":
    print(pof_within(age=40, years=3, beta=2.5, eta=45))
