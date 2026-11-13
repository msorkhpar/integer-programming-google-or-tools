from __future__ import annotations

from ortools.math_opt.python import mathopt


def add_energy_rows(model: mathopt.Model, x: dict, lifts: dict[str, tuple[int, int, int]]) -> dict:
    """For every stretch [a, b] from a release to a deadline: lifts that must happen inside it fit in it."""
    # TODO: write the rows first, then add them. Return them by (a, b).
    return {}


if __name__ == "__main__":
    model = mathopt.Model()
    lifts = {"breaker A": (6, 0, 8), "breaker B": (5, 2, 9)}
    x = {n: model.add_binary_variable(name=n) for n in lifts}
    print(sorted(add_energy_rows(model, x, lifts)))
