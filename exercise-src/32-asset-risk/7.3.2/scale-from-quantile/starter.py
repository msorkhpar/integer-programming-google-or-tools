import math


def scale_from_report(age: float, r: float, q: float, beta: float) -> float:
    """The scale on which a unit working at `age` fails within `r` years with chance `q`."""
    # TODO: solve R(age + r) / R(age) = 1 - q for eta.
    return r


if __name__ == "__main__":
    print(scale_from_report(25, 6, 0.1, 3.5))
