from __future__ import annotations

from ortools.math_opt.python import mathopt


def add_energy_rows(model: mathopt.Model, x: dict, lifts: dict[str, tuple[int, int, int]]) -> dict:
    """For every stretch [a, b] from a release to a deadline: lifts that must happen inside it fit in it."""
    rows = {}
    for a in sorted({r for _, r, _ in lifts.values()}):
        for b in sorted({d for _, _, d in lifts.values()}):
            inside = [n for n, (_, r, d) in lifts.items() if a <= r and d <= b]
            if b > a and inside:
                rows[a, b] = model.add_linear_constraint(
                    sum(lifts[n][0] * x[n] for n in inside) <= b - a, name=f"energy_{a}_{b}")
    return rows


if __name__ == "__main__":
    model = mathopt.Model()
    lifts = {"breaker A": (6, 0, 8), "breaker B": (5, 2, 9)}
    x = {n: model.add_binary_variable(name=n) for n in lifts}
    print(sorted(add_energy_rows(model, x, lifts)))
