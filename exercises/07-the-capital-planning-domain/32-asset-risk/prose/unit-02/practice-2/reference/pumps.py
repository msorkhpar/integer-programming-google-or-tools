import math

from scipy.integrate import quad


def mean_remaining_life(age: float, beta: float, eta: float) -> float:
    """Average years still ahead for pumps of this kind that are working at `age`."""

    def survival(t: float) -> float:
        return math.exp(-((t / eta) ** beta))

    def ratio(u: float) -> float:          # R(u) / R(age), without forming either tiny number
        return math.exp((age / eta) ** beta - (u / eta) ** beta)

    area, _ = quad(ratio, age, math.inf)
    return area


if __name__ == "__main__":
    print(mean_remaining_life(30, 2.5, 40))
