from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt

RENTAL_DAYS = 30           # days one mobile unit is rented for


@dataclass
class Fleet:
    model: mathopt.Model
    x: dict                # x[s, k] = 1: site s is served by unit k
    y: dict                # y[k] = 1: unit k is rented


def build(days: dict, units: int, *, ordered: bool = False) -> Fleet:
    """Serve every site with one rented unit; a unit's sites fit in its rental; rent as few as possible."""
    model = mathopt.Model(name="mobile units")
    x = {(s, k): model.add_binary_variable(name=f"x_{s}_{k}") for s in days for k in range(units)}
    y = {k: model.add_binary_variable(name=f"y_{k}") for k in range(units)}
    for s in days:
        model.add_linear_constraint(sum(x[s, k] for k in range(units)) == 1, name=f"served_{s}")
    for k in range(units):
        model.add_linear_constraint(sum(d * x[s, k] for s, d in days.items()) <= RENTAL_DAYS * y[k],
                                    name=f"rental_{k}")
    fleet = Fleet(model, x, y)
    if ordered:
        add_symmetry_breaking(fleet, days, units)
    model.minimize(sum(y.values()))
    return fleet


def add_symmetry_breaking(fleet: Fleet, days: dict, units: int) -> None:
    """Keep one numbering of the identical units: rented units come first, and sites fill them in order."""
    # TODO: rows that keep one numbering of the units.
    return None

def nodes(days: dict, units: int, ordered: bool) -> tuple[float, int]:
    result = mathopt.solve(build(days, units, ordered=ordered).model, mathopt.SolverType.HIGHS,
                           params=mathopt.SolveParameters(relative_gap_tolerance=0.0))
    return result.objective_value(), result.solve_stats.node_count


if __name__ == "__main__":
    days = {f"S{i:02d}": d for i, d in enumerate([16, 16, 14, 13, 13, 13, 12, 12, 12, 11, 11, 10, 9, 8])}
    for ordered in (False, True):
        units, count = nodes(days, 8, ordered)
        print(f"symmetry rows {ordered!s:5}  units rented {units:.0f}  nodes {count}")
