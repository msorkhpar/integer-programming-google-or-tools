from __future__ import annotations

import math


def discount(amount: float, year: int, first_year: int, rate: float) -> float:
    """What `amount` paid in calendar year `year` is worth on the first plan year."""
    return amount / (1 + rate) ** (year - first_year)


def npv(project: dict, forecast: dict, start: int, years: list[int], rate: float) -> float:
    """NPV on the first plan year (`years[0]`) of the project started in `start`."""
    # TODO: minus every cost, plus every benefit of the forecast, each discounted from its own year.
    return 0.0


def npv_table(snapshot: dict, forecast: dict) -> dict[tuple[str, int], int]:
    """{(project id, start year): NPV in whole $k} for every start in each project's window."""
    # TODO: one entry per start year in each project's window.
    return {}


if __name__ == "__main__":
    snapshot = {"years": [2027, 2028, 2029], "rate": 0.05,
                "projects": {"J1": {"cost": [100], "earliest": 2027, "latest": 2028}}}
    print(npv_table(snapshot, {"J1": {"benefits": [60, 60], "decay": 0.1}}))
