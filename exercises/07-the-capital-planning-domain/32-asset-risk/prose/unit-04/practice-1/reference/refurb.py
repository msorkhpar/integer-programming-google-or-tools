from dataclasses import dataclass


@dataclass(frozen=True)
class Pump:
    age: float          # in the plan's first year
    beta: float
    eta: float
    beta_new: float     # the new design's curve
    eta_new: float
    cof: float          # $k per failure


def failures(age: float, beta: float, eta: float) -> float:
    """Expected failures in the year from `age` to `age + 1`, failed units repaired and kept."""
    return ((age + 1) / eta) ** beta - (age / eta) ** beta


def yearly_cut(pump: Pump, years: list[int], start: int, duration: int) -> dict[int, float]:
    """Risk removed in each year ($k) by swapping the pump for the new design, work from `start`."""
    done = start + duration
    cut = {}
    for y in years:
        old_age = pump.age + (y - years[0])
        before = pump.cof * failures(old_age, pump.beta, pump.eta)
        if y < done:
            after = before
        else:
            after = pump.cof * failures(y - done, pump.beta_new, pump.eta_new)
        cut[y] = before - after
    return cut


if __name__ == "__main__":
    print(yearly_cut(Pump(35, 3.0, 40, 2.0, 60, 900), list(range(2027, 2033)), 2028, 1))
