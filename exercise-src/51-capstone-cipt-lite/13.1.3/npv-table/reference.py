from __future__ import annotations

import math


def discount(amount: float, year: int, first_year: int, rate: float) -> float:
    """What `amount` paid in calendar year `year` is worth on the first plan year."""
    return amount / (1 + rate) ** (year - first_year)


def npv(project: dict, forecast: dict, start: int, years: list[int], rate: float) -> float:
    """NPV on the first plan year (`years[0]`) of the project started in `start`."""
    first_year = years[0]
    value = 0.0
    for k, cost in enumerate(project["cost"]):
        value -= discount(cost, start + k, first_year, rate)
    in_service = start + len(project["cost"])
    shrink = (1 - forecast["decay"]) ** (start - project["earliest"])
    for k, benefit in enumerate(forecast["benefits"]):
        value += discount(benefit * shrink, in_service + k, first_year, rate)
    return value


def npv_table(snapshot: dict, forecast: dict) -> dict[tuple[str, int], int]:
    """{(project id, start year): NPV in whole $k} for every start in each project's window."""
    table = {}
    for pid, project in snapshot["projects"].items():
        for t in range(project["earliest"], project["latest"] + 1):
            value = npv(project, forecast[pid], t, snapshot["years"], snapshot["rate"])
            table[pid, t] = math.floor(value + 0.5)
    return table


if __name__ == "__main__":
    snapshot = {"years": [2027, 2028, 2029], "rate": 0.05,
                "projects": {"J1": {"cost": [100], "earliest": 2027, "latest": 2028}}}
    print(npv_table(snapshot, {"J1": {"benefits": [60, 60], "decay": 0.1}}))
