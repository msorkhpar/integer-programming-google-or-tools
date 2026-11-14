"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from ortools.math_opt.python import mathopt

from ranging import price_range


def kitchen(hours):
    """Prep hours: soups earn 4 per hour (at most 25), salads 1 per hour (at most 35)."""
    model = mathopt.Model(name="kitchen")
    soups = model.add_variable(lb=0, ub=25, name="soups")
    salads = model.add_variable(lb=0, ub=35, name="salads")
    row = model.add_linear_constraint(soups + salads <= hours, name="prep")
    model.maximize(4 * soups + salads)
    return model, row


for hours in (10, 40, 70):
    low, high = price_range(kitchen, hours, 0, 80)
    print(f"range around {hours} prep hours:", round(low, 2), round(high, 2))
