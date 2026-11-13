from __future__ import annotations

from ortools.math_opt.python import mathopt


def pumping_cut(stations: dict, demand: float, limit: float, price: float, plan: dict[str, int], x: dict):
    """The pumping cost of a fixed plan, and the optimality cut its LP gives, in the master's x."""
    sub = mathopt.Model(name="pumping")
    flow = {j: sub.add_variable(lb=0, name=f"flow_{j}") for j in stations}
    buy = sub.add_variable(lb=0, name="buy")
    need = sub.add_linear_constraint(
        sum(flow.values()) + buy >= demand + sum(s["refill"] * plan[j] for j, s in stations.items()), name="need")
    caps = {j: sub.add_linear_constraint(flow[j] <= s["capacity"] * plan[j], name=f"cap_{j}")
            for j, s in stations.items()}
    most = sub.add_linear_constraint(buy <= limit, name="limit")
    sub.minimize(sum(s["energy"] * flow[j] for j, s in stations.items()) + price * buy)
    result = mathopt.solve(sub, mathopt.SolverType.GLOP)
    cut = result.dual_values(need) * (demand + sum(s["refill"] * x[j] for j, s in stations.items()))
    cut += sum(result.dual_values(caps[j]) * s["capacity"] * x[j] for j, s in stations.items())
    cut += result.dual_values(most) * limit
    return result.objective_value(), cut


if __name__ == "__main__":
    master = mathopt.Model()
    x = {"A": master.add_binary_variable(name="A")}
    print(pumping_cut({"A": {"capacity": 60, "energy": 2.0, "refill": 5}}, 100, 500, 6.0, {"A": 1}, x))
