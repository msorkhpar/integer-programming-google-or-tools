from __future__ import annotations

from ortools.sat.python import cp_model


def buy_routes(routes: dict[str, int], offers: list[tuple[int, int, int]],
               city_limit: int) -> tuple[int, dict[str, tuple[int, int, int]]]:
    """(total price, route -> (seats, operator, price)) of the cheapest set of offers."""
    # TODO: seats, a city Boolean and a price per route, tied to the offers by a table, seats for
    # every rider, the city's limit, and minimize the total price. Placeholders below.
    return -1, {r: (0, 0, 0) for r in routes}


if __name__ == "__main__":
    print(buy_routes({"hill": 25, "river": 40}, [(30, 0, 100), (30, 1, 70), (50, 0, 150)], 1))
