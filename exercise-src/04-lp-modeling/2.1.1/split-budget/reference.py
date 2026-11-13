from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt

TOL = 1e-6


@dataclass(frozen=True)
class Terminal:
    name: str
    value: float          # value returned per $k spent
    hours_per_k: float    # dock-crew hours per $k of work
    hours: float          # dock-crew hours available
    floor: float = 0      # least it must get, $k (0: no floor)


def split(terminals: list[Terminal], budget: float):
    """Solve the split LP with GLOP. Returns (status, value, amounts, full rows)."""
    model = mathopt.Model(name="terminal split")
    x = {t.name: model.add_variable(lb=0, name=f"x_{t.name}") for t in terminals}
    rows = [model.add_linear_constraint(sum(x.values()) <= budget, name="budget")]
    for t in terminals:
        rows.append(model.add_linear_constraint(t.hours_per_k * x[t.name] <= t.hours, name=f"labour_{t.name}"))
        if t.floor > 0:
            rows.append(model.add_linear_constraint(x[t.name] >= t.floor, name=f"floor_{t.name}"))
    model.maximize(sum(t.value * x[t.name] for t in terminals))
    result = mathopt.solve(model, mathopt.SolverType.GLOP)
    status = result.termination.reason.name
    if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
        return status, None, None, None
    values = result.variable_values()
    amounts = {name: values[v] for name, v in x.items()}
    full = set()
    for row in rows:
        a = sum(term.coefficient * values[term.variable] for term in row.terms())
        if abs(a - row.upper_bound) <= TOL or abs(a - row.lower_bound) <= TOL:
            full.add(row.name)
    return status, result.objective_value(), amounts, full


if __name__ == "__main__":
    port = [Terminal("north", 1.2, 2, 400), Terminal("south", 0.9, 1, 300), Terminal("east", 0.7, 4, 800)]
    print(split(port, 600))
