from __future__ import annotations

from ortools.math_opt.python import mathopt


def fewest_refusals(vessels: dict, berths: dict) -> tuple[list[str], dict[str, int]]:
    """Refuse as few berthing requests as possible; every vessel still berths once, inside its window."""
    model = mathopt.Model(name="port")
    at = {(v, d): model.add_binary_variable(name=f"at_{v}_{d}")
          for v, (first, last, _) in vessels.items() for d in range(first, last + 1) if d in berths}
    refuse = {v: model.add_binary_variable(name=f"refuse_{v}") for v in vessels}
    for v, (first, last, wanted) in vessels.items():
        model.add_linear_constraint(mathopt.fast_sum(x for (w, _), x in at.items() if w == v) == 1, name=f"berth_{v}")
        model.add_linear_constraint(at.get((v, wanted), 0) + refuse[v] >= 1, name=f"request_{v}")
    for d, count in berths.items():
        model.add_linear_constraint(mathopt.fast_sum(x for (_, e), x in at.items() if e == d) <= count, name=f"berths_{d}")
    model.minimize(mathopt.fast_sum(refuse.values()))
    result = mathopt.solve(model, mathopt.SolverType.HIGHS,
                            params=mathopt.SolveParameters(relative_gap_tolerance=0.0))
    values = result.variable_values()
    refused = sorted(v for v, r in refuse.items() if values[r] > 0.5)
    schedule = {v: d for (v, d), x in at.items() if values[x] > 0.5}
    return refused, schedule


if __name__ == "__main__":
    print(fewest_refusals({"Aurora": (1, 2, 1), "Borealis": (1, 2, 1)}, {1: 1, 2: 1}))
