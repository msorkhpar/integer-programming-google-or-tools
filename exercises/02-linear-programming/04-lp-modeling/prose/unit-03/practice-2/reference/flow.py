from __future__ import annotations

from ortools.math_opt.python import mathopt

Arc = tuple[str, str]


def ship(supply: dict[str, float], demand: dict[str, float], arcs: dict[Arc, tuple[float, float]]):
    """Cheapest flow meeting every demand. Returns (status, cost, flow by arc)."""
    model = mathopt.Model(name="food bank")
    f = {(i, j): model.add_variable(lb=0, ub=cap, name=f"f_{i}_{j}") for (i, j), (_, cap) in arcs.items()}
    nodes = {n for arc in arcs for n in arc} | set(supply) | set(demand)
    for n in sorted(nodes):
        net_in = sum(f[i, j] for (i, j) in arcs if j == n) - sum(f[i, j] for (i, j) in arcs if i == n)
        if n in supply:
            model.add_linear_constraint(-net_in <= supply[n], name=f"supply_{n}")
        elif n in demand:
            model.add_linear_constraint(net_in == demand[n], name=f"demand_{n}")
        else:
            model.add_linear_constraint(net_in == 0, name=f"balance_{n}")
    model.minimize(sum(cost * f[a] for a, (cost, _) in arcs.items()))
    result = mathopt.solve(model, mathopt.SolverType.GLOP)
    status = result.termination.reason.name
    if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
        return status, None, None
    return status, result.objective_value(), {a: result.variable_values(v) for a, v in f.items()}


if __name__ == "__main__":
    print(ship({"W1": 10}, {"P1": 10}, {("W1", "P1"): (3, 20)}))
