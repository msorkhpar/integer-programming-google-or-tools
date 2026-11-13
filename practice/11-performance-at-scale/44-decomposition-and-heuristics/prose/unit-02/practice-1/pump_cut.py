from __future__ import annotations

from ortools.math_opt.python import mathopt


def pumping_cut(stations: dict, demand: float, limit: float, price: float, plan: dict[str, int], x: dict):
    """The pumping cost of a fixed plan, and the optimality cut its LP gives, in the master's x."""
    # TODO: write the subproblem and its cut first, then build, solve and return them.
    return 0.0, mathopt.LinearExpression()


if __name__ == "__main__":
    master = mathopt.Model()
    x = {"A": master.add_binary_variable(name="A")}
    print(pumping_cut({"A": {"capacity": 60, "energy": 2.0, "refill": 5}}, 100, 500, 6.0, {"A": 1}, x))
