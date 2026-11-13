"""Lesson 6.6.2: weights on the breakpoints, with and without the binaries that keep them on two neighbours.

MathOpt's Python model has no SOS method in OR-Tools 9.15, so the "two neighbours" rule (SOS2) is
written with one binary per segment. The program checks the API, then fixes x on the falling-tier
credit line of lesson 6.6.1 and asks how low and how high y may go with each version of the rows.
"""

from ortools.math_opt.python import mathopt
from ortools.sat.python import cp_model

from credit_line import FALLING
from piecewise import add_lambda
from selection import solve_highs

POINTS = (1000, 2000, 3500, 4500)


def y_range(curve, x_value, binaries):
    ends = []
    for sense in ("min", "max"):
        model = mathopt.Model()
        piece = add_lambda(model, curve, "c", binaries=binaries)
        model.add_linear_constraint(piece.x == x_value)
        model.minimize(piece.y) if sense == "min" else model.maximize(piece.y)
        ends.append(solve_highs(model).objective_value())
    return f"{ends[0]:.0f}" if abs(ends[0] - ends[1]) < 1e-6 else f"{ends[0]:.0f} to {ends[1]:.0f}"


if __name__ == "__main__":
    print("MathOpt Model methods naming SOS:", [m for m in dir(mathopt.Model) if "sos" in m.lower()])
    print("CP-SAT CpModel methods naming SOS:", [m for m in dir(cp_model.CpModel) if "sos" in m.lower()])
    print("falling tiers, breakpoints", list(zip(FALLING.xs, FALLING.ys)))
    print("x     | f(x) | weights only  | weights + segment binaries")
    for x in POINTS:
        print(f"{x:<5} | {FALLING(x):4.0f} | {y_range(FALLING, x, False):13} | {y_range(FALLING, x, True)}")
