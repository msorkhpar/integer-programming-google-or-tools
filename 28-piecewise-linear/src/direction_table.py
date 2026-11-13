"""Lesson 6.6.1: when do segment variables alone give y = f(x)? It depends on the shape and on the push.

For each tiered curve, the program fixes x, lets the solver move y the way the model's objective
pushes it (down for a cost, up for a value), and compares the y it returns with the true f(x).
"""

from ortools.math_opt.python import mathopt

from credit_line import FALLING, RISING
from piecewise import add_segments
from selection import solve_highs

POINTS = (1000, 2000, 3500, 4500)


def pushed(curve, x_value, push):
    """The y the segment form returns at x, when the objective pushes y `push` ('down' or 'up')."""
    model = mathopt.Model()
    piece = add_segments(model, curve, "c")
    model.add_linear_constraint(piece.x == x_value)
    model.minimize(piece.y) if push == "down" else model.maximize(piece.y)
    return solve_highs(model).objective_value()


if __name__ == "__main__":
    print("curve    shape    y is pushed | x =  1000   2000   3500   4500 | exact?")
    for name, curve in (("rising", RISING), ("falling", FALLING)):
        shape = "convex" if curve.convex() else "concave"
        print(f"{name:8} {shape:8} f(x)        |      " + "  ".join(f"{curve(x):5.0f}" for x in POINTS))
        for push in ("down", "up"):
            got = [pushed(curve, x, push) for x in POINTS]
            exact = all(abs(g - curve(x)) < 1e-6 for g, x in zip(got, POINTS))
            print(f"{'':17} {push:11} |      " + "  ".join(f"{g:5.0f}" for g in got) + f" | {'yes' if exact else 'no'}")
