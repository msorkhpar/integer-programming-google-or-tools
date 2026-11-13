"""From an asset-health prediction to a number a model can use: next year's expected failure cost."""

import math

from gridcap import generate

tiny = generate("tiny")


def cumulative_pof(age: float, beta: float, eta: float) -> float:
    """Weibull probability that the asset has failed by `age` years."""
    return 1 - math.exp(-((age / eta) ** beta))


def next_year_pof(age: float, beta: float, eta: float) -> float:
    """Probability it fails in the coming year, given that it is still working at `age`."""
    survived = 1 - cumulative_pof(age, beta, eta)
    return (cumulative_pof(age + 1, beta, eta) - cumulative_pof(age, beta, eta)) / survived


def expected_failure_cost(asset, age: float | None = None) -> float:
    """PoF next year times the consequence of failure, in $k."""
    age = asset.age if age is None else age
    return next_year_pof(age, asset.weibull_beta, asset.weibull_eta) * asset.cof


if __name__ == "__main__":
    print(f"{'asset':5} {'age':>3} {'RUL':>3} {'PoF next yr':>11} {'CoF $k':>7} {'risk $k/yr':>10}")
    for a in tiny.assets:
        pof = next_year_pof(a.age, a.weibull_beta, a.weibull_eta)
        print(f"{a.asset_id:5} {a.age:>3} {a.rul:>3} {pof:>11.3f} {a.cof:>7,} {expected_failure_cost(a):>10.1f}")
