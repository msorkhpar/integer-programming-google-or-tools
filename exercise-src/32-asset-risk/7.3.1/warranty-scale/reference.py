import math


def required_scale(warranty_years: float, max_share: float, beta: float) -> float:
    """The smallest characteristic life (years) for which at most `max_share` fail within the warranty."""
    return warranty_years / (-math.log(1 - max_share)) ** (1 / beta)


if __name__ == "__main__":
    print(required_scale(5, 0.02, 2.5))
