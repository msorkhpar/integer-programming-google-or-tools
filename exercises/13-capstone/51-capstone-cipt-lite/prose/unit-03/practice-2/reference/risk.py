from __future__ import annotations

import math


def scale_from_rul(age: float, rul: float, beta: float) -> float:
    """The Weibull scale for which `rul` is the median remaining life at this age."""
    return (((age + rul) ** beta - age ** beta) / math.log(2)) ** (1 / beta)


def expected_failures(age: float, beta: float, eta: float) -> float:
    """Expected failures in the year from `age` to `age + 1`, failures repaired as they come."""
    return ((age + 1) / eta) ** beta - (age / eta) ** beta


def age_in(year: int, asset: dict, first_year: int, start: int | None, duration: int) -> float:
    """The asset's age in `year`: it ages until the work ends, then keeps `keep` of the age it reached."""
    grown = asset["age"] + (year - first_year)
    if start is None or year < start + duration:
        return grown
    done = start + duration
    return asset["keep"] * (asset["age"] + (done - first_year)) + (year - done)


def risk_removed(asset: dict, start: int, duration: int, years: list[int], window: int, rate: float) -> float:
    """Discounted risk removed over `window` years from the first plan year `years[0]`, $k."""
    first_year = years[0]
    eta = scale_from_rul(asset["age"], asset["rul"], asset["beta"])
    total = 0.0
    for year in range(first_year, first_year + window):
        without = expected_failures(age_in(year, asset, first_year, None, duration), asset["beta"], eta)
        with_work = expected_failures(age_in(year, asset, first_year, start, duration), asset["beta"], eta)
        total += asset["cof"] * (without - with_work) / (1 + rate) ** (year - first_year)
    return total


def risk_table(snapshot: dict, assets: dict, window: int) -> dict[tuple[str, int], float]:
    """{(project id, start year): risk removed in $k, rounded to 0.001}."""
    table = {}
    for pid, project in snapshot["projects"].items():
        for t in range(project["earliest"], project["latest"] + 1):
            value = risk_removed(assets[pid], t, len(project["cost"]), snapshot["years"], window,
                                 snapshot["rate"])
            table[pid, t] = round(value, 3)
    return table


if __name__ == "__main__":
    snapshot = {"years": [2027, 2028, 2029], "rate": 0.05,
                "projects": {"J1": {"cost": [100], "earliest": 2027, "latest": 2028}}}
    assets = {"J1": {"age": 30, "beta": 3.0, "rul": 12, "eta": 40.0, "cof": 500, "keep": 0.0}}
    print(risk_table(snapshot, assets, window=6))
