from __future__ import annotations

from ortools.sat.python import cp_model


def buy_routes(routes: dict[str, int], offers: list[tuple[int, int, int]],
               city_limit: int) -> tuple[int, dict[str, tuple[int, int, int]]]:
    """(total price, route -> (seats, operator, price)) of the cheapest set of offers."""
    model = cp_model.CpModel()
    seats, city, price = {}, {}, {}
    for r, riders in routes.items():
        seats[r] = model.new_int_var(min(o[0] for o in offers), max(o[0] for o in offers), f"seats_{r}")
        city[r] = model.new_bool_var(f"city_{r}")
        price[r] = model.new_int_var(min(o[2] for o in offers), max(o[2] for o in offers), f"price_{r}")
        model.add_allowed_assignments([seats[r], city[r], price[r]], offers)
        model.add(seats[r] >= riders)
    model.add(sum(city.values()) <= city_limit)
    model.minimize(sum(price.values()))
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1
    solver.solve(model)
    return round(solver.objective_value), {
        r: (solver.value(seats[r]), solver.value(city[r]), solver.value(price[r])) for r in routes}


if __name__ == "__main__":
    print(buy_routes({"hill": 25, "river": 40}, [(30, 0, 100), (30, 1, 70), (50, 0, 150)], 1))
