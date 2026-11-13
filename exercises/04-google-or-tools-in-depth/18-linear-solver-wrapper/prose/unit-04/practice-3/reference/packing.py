from __future__ import annotations

from ortools.math_opt.python import mathopt


def fewest_crews(sizes: list[int], season: int):
    """Pack every job (size in crew-months) into seasons of `season` crew-months, using as few as possible.

    Returns (number of seasons, [[job indices] for each season used]), or None if no packing exists.
    """
    model = mathopt.Model(name="seasons")
    jobs, seasons = range(len(sizes)), range(len(sizes))          # one season per job is always enough
    x = {(i, b): model.add_binary_variable(name=f"x_{i}_{b}") for i in jobs for b in seasons}
    y = {b: model.add_binary_variable(name=f"y_{b}") for b in seasons}
    for i in jobs:
        model.add_linear_constraint(sum(x[i, b] for b in seasons) == 1, name=f"once_{i}")
    for b in seasons:
        model.add_linear_constraint(sum(sizes[i] * x[i, b] for i in jobs) <= season * y[b], name=f"cap_{b}")
    model.minimize(sum(y.values()))
    result = mathopt.solve(model, mathopt.SolverType.CP_SAT)
    if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
        return None
    packing = [[i for i in jobs if result.variable_values(x[i, b]) > 0.5] for b in seasons]
    return round(result.objective_value()), [p for p in packing if p]


if __name__ == "__main__":
    print(fewest_crews([3, 3, 2, 2, 2, 2], 7))
