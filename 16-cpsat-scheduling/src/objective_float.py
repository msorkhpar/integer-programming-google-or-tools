"""Lesson 4.5.3: CP-SAT's objective_value is a float, so turn it into a whole number with round().

A crew rents a chipper for at least 4 days and a bucket lift for at least 28. The first model prices
them in $k per day (0.1 and 0.7, float coefficients); the second in $100 per day (1 and 7, whole
numbers). GridCap is fictional, and so are the rental prices.
"""

from ortools.sat.python import cp_model

from cpsat_run import solve


def rent(prices: list[float], unit: str) -> None:
    model = cp_model.CpModel()
    chipper = model.new_int_var(4, 30, "chipper_days")
    lift = model.new_int_var(28, 30, "lift_days")
    cost = prices[0] * chipper + prices[1] * lift
    model.minimize(cost)
    solver, status = solve(model)
    value = solver.objective_value
    print(f"prices {prices} {unit}/day: {status}, objective_value {value!r} ({type(value).__name__})")
    print(f"  int() {int(value)}   round() {round(value)}")
    if all(float(p).is_integer() for p in prices):
        print(f"  solver.value(cost) {solver.value(cost)!r} ({type(solver.value(cost)).__name__})")


if __name__ == "__main__":
    rent([0.1, 0.7], "$k")
    rent([1, 7], "$100")
