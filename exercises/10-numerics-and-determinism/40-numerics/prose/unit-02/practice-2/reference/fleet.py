from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt

# Each order: (price, value), in dollars. Invented teaching data, not a real agency's.
ORDERS = {
    "electric": (4_200_000, 5_100_000),
    "hybrid": (2_600_000, 3_000_000),
    "diesel": (1_500_000, 1_650_000),
    "shuttle": (450_000, 520_000),
}
BUDGET = 7_000_000      # dollars
LIMIT = 900_000         # the most the overdraft may be, dollars
FEE = 150_000           # to arrange an overdraft, dollars


@dataclass
class Fleet:
    model: mathopt.Model
    buy: dict[str, mathopt.Variable]
    overdraft: mathopt.Variable
    arranged: mathopt.Variable


def build_raw() -> Fleet:
    """The colleague's model: objective in dollars, budget rows and overdraft in $M, M = 1e9."""
    model = mathopt.Model(name="fleet, mixed units")
    buy = {name: model.add_binary_variable(name=f"buy_{name}") for name in ORDERS}
    overdraft = model.add_variable(lb=0, name="overdraft")
    arranged = model.add_binary_variable(name="arranged")
    model.maximize(sum(value * buy[n] for n, (_, value) in ORDERS.items()) - FEE * arranged)
    model.add_linear_constraint(
        sum(price / 1e6 * buy[n] for n, (price, _) in ORDERS.items()) <= BUDGET / 1e6 + overdraft, name="budget")
    model.add_linear_constraint(overdraft <= LIMIT / 1e6, name="limit")
    model.add_linear_constraint(overdraft <= 1e9 * arranged, name="switch")
    return Fleet(model, buy, overdraft, arranged)


def build_scaled() -> Fleet:
    """The same model with every amount in $k, and the smallest valid M."""
    model = mathopt.Model(name="fleet, $k")
    buy = {name: model.add_binary_variable(name=f"buy_{name}") for name in ORDERS}
    overdraft = model.add_variable(lb=0, name="overdraft")
    arranged = model.add_binary_variable(name="arranged")
    model.maximize(sum(value / 1000 * buy[n] for n, (_, value) in ORDERS.items()) - FEE / 1000 * arranged)
    model.add_linear_constraint(
        sum(price / 1000 * buy[n] for n, (price, _) in ORDERS.items()) <= BUDGET / 1000 + overdraft, name="budget")
    model.add_linear_constraint(overdraft <= LIMIT / 1000, name="limit")
    smallest_valid_m = LIMIT / 1000      # the limit row already caps the overdraft here
    model.add_linear_constraint(overdraft <= smallest_valid_m * arranged, name="switch")
    return Fleet(model, buy, overdraft, arranged)


if __name__ == "__main__":
    fleet = build_scaled()
    result = mathopt.solve(fleet.model, mathopt.SolverType.HIGHS)
    print(result.termination.reason.name, result.objective_value())
