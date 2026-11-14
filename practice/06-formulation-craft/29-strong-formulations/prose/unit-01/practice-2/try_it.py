"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from ortools.math_opt.python import mathopt

from compare import compare


def formulation(rows, sense="max"):
    def build(objective):
        model = mathopt.Model()
        u = model.add_variable(lb=0, ub=1, name="u")
        v = model.add_variable(lb=0, ub=1, name="v")
        for row in rows:
            model.add_linear_constraint(row(u, v))
        expr = objective[0] * u + objective[1] * v
        model.maximize(expr) if sense == "max" else model.minimize(expr)
        return model
    return build


tight = formulation([lambda u, v: u + v <= 1])
loose = formulation([lambda u, v: 3 * u + 3 * v <= 5])
tilted = formulation([lambda u, v: 3 * u + v <= 3])
objs = [(2, 1), (1, 4)]

print("tight vs loose:", compare(tight, loose, objs))
print("loose vs tight:", compare(loose, tight, objs))
print("tight vs tight:", compare(tight, tight, objs))
print("tight vs tilted:", compare(tight, tilted, objs))
