from dataclasses import dataclass


@dataclass(frozen=True)
class Main:
    age: float          # in the plan's first year
    beta: float
    eta: float
    cof: float          # $k per failure


def failures(age: float, beta: float, eta: float) -> float:
    return ((age + 1) / eta) ** beta - (age / eta) ** beta


def yearly_cut(main: Main, years: list[int], start: int, duration: int, keep: float) -> dict[int, float]:
    """Risk removed in each year ($k); `years` starts at the plan's first year."""
    done = start + duration
    cut = {}
    for y in years:
        old = main.age + (y - years[0])
        new = old if y < done else keep * (main.age + done - years[0]) + (y - done)
        cut[y] = main.cof * (failures(old, main.beta, main.eta) - failures(new, main.beta, main.eta))
    return cut


def coefficients(main: Main, starts: list[int], first_year: int, duration: int, keep: float,
                 service_years: int, rate: float) -> dict[int, float]:
    """For each start year: the risk removed over its service years, discounted to `first_year`."""
    # TODO: sum each start's yearly reductions up to the end of its service period, discounted.
    return {s: -1.0 for s in starts}


if __name__ == "__main__":
    print(coefficients(Main(48, 2.8, 45, 1_200), [2027, 2028, 2029], 2027, 2, 0.0, 10, 0.06))
