import math


def scale_from_report(age: float, r: float, q: float, beta: float) -> float:
    """The scale on which a unit working at `age` fails within `r` years with chance `q`."""
    return (((age + r) ** beta - age ** beta) / -math.log(1 - q)) ** (1 / beta)


if __name__ == "__main__":
    print(scale_from_report(25, 6, 0.1, 3.5))
