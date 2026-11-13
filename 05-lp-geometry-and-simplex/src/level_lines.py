"""Slide the objective's level line across the region: the last point it touches is a vertex."""

from math import comb

from ortools.math_opt.python import mathopt

from split_lp import VALUE, build
from vertices import vertices

LETTER = {(0.0, 0.0): "A", (24.0, 0.0): "B", (12.0, 18.0): "C", (10.0, 20.0): "D", (0.0, 20.0): "E"}


def value(point, c=VALUE) -> float:
    return c[0] * point[0] + c[1] * point[1]


def touches(level: float, c=VALUE) -> str:
    """Whether the line c.x = level meets the region: it does when level lies between the vertices' values."""
    values = [value(p, c) for p in vertices()]
    if level > max(values) + 1e-9 or level < min(values) - 1e-9:
        return "misses the region"
    on = ", ".join(LETTER[p] for p in vertices() if abs(value(p, c) - level) < 1e-9)
    if abs(level - max(values)) < 1e-9:
        return f"touches the region only at {on}" if "," not in on else f"touches the region along {on}"
    return "crosses the region" + (f", through vertex {on}" if on else "")


if __name__ == "__main__":
    for p in sorted(vertices(), key=value):
        print(f"{LETTER[p]} ({p[0]:g}, {p[1]:g}): 5d + 4t = {value(p):g}")
    for level in (60, 100, 130, 132, 140):
        print(f"level {level}: {touches(level)}")
    tie = (4, 4)
    best = max(value(p, tie) for p in vertices())
    print(f"objective 4d + 4t: best {best:g} at", [LETTER[p] for p in vertices() if value(p, tie) == best])
    print(f"level {best:g} of 4d + 4t: {touches(best, tie)}")
    model, x = build()
    result = mathopt.solve(model, mathopt.SolverType.GLOP)
    print(f"GLOP: {result.termination.reason.name}, d = {result.variable_values(x['d']):g}, "
          f"t = {result.variable_values(x['t']):g}, value {result.objective_value():g}")
    for n, m in ((2, 3), (10, 20), (50, 100), (100, 200)):
        print(f"{n} variables, {m} rows: {comb(n + m, n):.3g} ways to pick {n} tight rows")
