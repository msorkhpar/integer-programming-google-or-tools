from __future__ import annotations

from ortools.sat.python import cp_model

SCALE = 100          # hundredths of a million: every cost and the budget is a whole number of these


def pick(values: list[float], costs: list[float], budget: float) -> list[int]:
    """Indices of the repairs to fund, in increasing order: most value with total cost <= budget."""
    model = cp_model.CpModel()
    x = [model.new_bool_var(f"x_{i}") for i in range(len(values))]
    whole = [round(c * SCALE) for c in costs]
    model.add(sum(w * xi for w, xi in zip(whole, x)) <= round(budget * SCALE))
    model.maximize(sum(round(v * SCALE) * xi for v, xi in zip(values, x)))
    solver = cp_model.CpSolver()
    solver.solve(model)
    return [i for i in range(len(x)) if solver.value(x[i])]


if __name__ == "__main__":
    print(pick([3, 4, 5], [0.5, 0.65, 1.2], 1.15))
