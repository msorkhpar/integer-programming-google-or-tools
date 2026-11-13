import math


def log_likelihood(beta: float, eta: float, failed: list[float], working: list[float]) -> float:
    """Log-likelihood of a Weibull(beta, eta) for failure ages and current ages of units still working."""
    total = 0.0
    # TODO: add each failed unit's log density and each working unit's log survival.
    return total


if __name__ == "__main__":
    print(log_likelihood(3.0, 45.0, [18, 30], [35, 35]))
