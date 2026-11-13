from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt


@dataclass(frozen=True)
class Pit:
    name: str
    price: float      # $ per ton
    fines: float      # fines content, % of weight
    tons: float       # tons the pit can supply


def mix(pits: list[Pit], tons: float, low: float, high: float):
    """Cheapest blend of `tons` tons whose average fines content lies in [low, high]."""
    model = mathopt.Model(name="gravel blend")
    t = {p.name: model.add_variable(lb=0, ub=p.tons, name=f"t_{p.name}") for p in pits}
    model.add_linear_constraint(sum(t.values()) == tons, name="tons")
    model.add_linear_constraint(sum((p.fines - high) * t[p.name] for p in pits) <= 0, name="fines_max")
    model.add_linear_constraint(sum((p.fines - low) * t[p.name] for p in pits) >= 0, name="fines_min")
    model.minimize(sum(p.price * t[p.name] for p in pits))
    result = mathopt.solve(model, mathopt.SolverType.GLOP)
    status = result.termination.reason.name
    if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
        return status, None, None
    return status, result.objective_value(), {name: result.variable_values(v) for name, v in t.items()}


if __name__ == "__main__":
    pits = [Pit("A", 12, 4, 500), Pit("B", 9, 9, 600), Pit("C", 7, 14, 400)]
    print(mix(pits, 1000, 6, 10))
