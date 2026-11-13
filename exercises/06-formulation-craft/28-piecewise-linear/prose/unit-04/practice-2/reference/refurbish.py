from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt

DEPTHS = (0.0, 0.25, 0.5, 0.75, 1.0)


@dataclass(frozen=True)
class Pump:
    pid: str
    age: float
    beta: float
    eta: float
    cof: float      # $k per failure
    capex: float    # $k for a full refurbishment


def value_points(pump: Pump, horizon: float) -> list[float]:
    """The failure cost avoided over `horizon` years at each depth of DEPTHS, in $k."""
    def failures(age: float) -> float:
        return ((age + horizon) / pump.eta) ** pump.beta - (age / pump.eta) ** pump.beta

    return [pump.cof * (failures(pump.age) - failures((1 - d) * pump.age)) for d in DEPTHS]


def plan(pumps: list[Pump], fund: float, horizon: float) -> tuple[float, dict[str, float]]:
    """The best total value within the fund, and the depth chosen for each pump."""
    model = mathopt.Model(name="refurbishment")
    depth, worth = {}, {}
    for p in pumps:
        v = value_points(p, horizon)
        rises = [v[k + 1] - v[k] for k in range(len(v) - 1)]
        if all(a >= b for a, b in zip(rises, rises[1:])):          # concave and pushed up: lines suffice
            d = model.add_variable(lb=0, ub=1, name=f"d_{p.pid}")
            y = model.add_variable(lb=0, name=f"v_{p.pid}")
            for k, rise in enumerate(rises):
                model.add_linear_constraint(y <= v[k] + rise / 0.25 * (d - DEPTHS[k]), name=f"below_{p.pid}_{k}")
            depth[p.pid], worth[p.pid] = d, y
        else:                                                      # quarters used strictly in order
            used = [model.add_variable(lb=0, ub=1, name=f"used_{p.pid}_{k}") for k in range(len(rises))]
            for k in range(len(rises) - 1):
                done = model.add_binary_variable(name=f"done_{p.pid}_{k}")
                model.add_linear_constraint(used[k + 1] <= done, name=f"then_{p.pid}_{k}")
                model.add_linear_constraint(done <= used[k], name=f"done_{p.pid}_{k}")
            depth[p.pid] = 0.25 * sum(used)
            worth[p.pid] = sum(rise * u for rise, u in zip(rises, used))
    model.add_linear_constraint(sum(p.capex * depth[p.pid] for p in pumps) <= fund, name="fund")
    model.maximize(sum(worth.values()))
    result = mathopt.solve(model, mathopt.SolverType.HIGHS,
                           params=mathopt.SolveParameters(relative_gap_tolerance=0.0))
    chosen = {pid: mathopt.evaluate_expression(d + 0, result.variable_values()) for pid, d in depth.items()}
    return result.objective_value(), chosen


if __name__ == "__main__":
    fleet = [Pump("North", 30, 3.2, 40, 500, 400), Pump("South", 35, 1.4, 45, 900, 500)]
    print([round(v, 1) for v in value_points(fleet[0], 3)])
    print(plan(fleet, 500, 3))
