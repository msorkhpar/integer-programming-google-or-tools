import math

from scipy.integrate import quad


def mean_remaining_life(age: float, beta: float, eta: float) -> float:
    """Average years still ahead for pumps of this kind that are working at `age`."""

    def survival(t: float) -> float:
        return math.exp(-((t / eta) ** beta))

    # TODO: the area under the survival curve after `age`, per pump still working at `age`.
    return 0.0


if __name__ == "__main__":
    print(mean_remaining_life(30, 2.5, 40))
