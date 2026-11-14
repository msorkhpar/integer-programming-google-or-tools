"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from ortools.math_opt.python import mathopt

from audit import audit


def variant(extra_pair: bool, one_row: bool):
    def build(integer):
        model = mathopt.Model()
        p, q, r = (model.add_variable(lb=0, ub=1, is_integer=integer, name=n) for n in "pqr")
        if one_row:
            model.add_linear_constraint(p + q + r <= 1)
        else:
            model.add_linear_constraint(2 * p + 2 * q + 2 * r <= 3)
        if extra_pair:
            model.add_linear_constraint(q + r <= 1)
        model.maximize(6 * p + 5 * q + 2 * r)
        return model
    return build


variants = {"weak": variant(False, False), "pair q-r": variant(True, False), "clique": variant(False, True)}
for line in audit(variants, optimum=6):
    print(f"{line['name']}: vars {line['variables']} rows {line['rows']} lp {line['lp']:.3f}"
          f" root {line['root']:.3f} closed {line['closed']:.3f}")
