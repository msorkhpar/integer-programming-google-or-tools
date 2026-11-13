from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt


@dataclass(frozen=True)
class Device:
    name: str
    beds: int         # beds kept in service
    safety: int       # audit points
    cost: int         # $k


def augmented_choice(devices: list[Device], budget: int, floor: int, span: float, rho: float = 1e-3):
    """(sorted names, slack) of the most beds with at least `floor` safety points, or None."""
    model = mathopt.Model(name="devices")
    pick = {d.name: model.add_binary_variable(name=f"replace_{d.name}") for d in devices}
    model.add_linear_constraint(sum(d.cost * pick[d.name] for d in devices) <= budget, name="budget")
    above = model.add_variable(lb=0.0, name="above_floor")
    model.add_linear_constraint(sum(d.safety * pick[d.name] for d in devices) - above == floor, name="safety_floor")
    model.maximize(sum(d.beds * pick[d.name] for d in devices) + (rho / span) * above)
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
        return None
    values = result.variable_values()
    return tuple(sorted(n for n, v in pick.items() if values[v] > 0.5)), values[above]


if __name__ == "__main__":
    ward = [Device("Ventilator", 12, 4, 60), Device("Monitor", 8, 7, 30), Device("Alarm Panel", 0, 5, 10)]
    print(augmented_choice(ward, 100, 8, span=16))
