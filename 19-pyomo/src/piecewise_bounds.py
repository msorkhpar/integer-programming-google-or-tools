"""Lesson 5.1.4: Piecewise needs its x variable bounded, and inside the breakpoints' range.

GridCap is a fictional utility's portfolio. The contractor price curve of contractor_model.py
(breakpoints at 0, 10, 20 and 40 crew-months) on a model of its own: each contractor month is worth
$100k to the planners, so the objective pushes the months bought up and their cost down.
"""

import pyomo.environ as pyo

from contractor_model import COST, MONTHS
from pyomo_timing import highs


def months_bought(upper):
    """Build the curve with `bought` bounded by (0, upper), solve, and say what came back."""
    m = pyo.ConcreteModel()
    m.bought = pyo.Var(bounds=(0, upper))                     # contractor crew-months
    m.contract = pyo.Var(bounds=(0, None))                    # their cost, $k
    try:
        m.tiers = pyo.Piecewise(m.contract, m.bought, pw_pts=MONTHS, f_rule=COST,
                                pw_constr_type="LB", pw_repn="INC")
    except ValueError as error:
        return f"ValueError: {str(error).splitlines()[0]}"
    m.gain = pyo.Objective(expr=100 * m.bought - m.contract, sense=pyo.maximize)
    highs().solve(m)
    return f"bought {m.bought.value:g}, contract {m.contract.value:g}"


for upper in (40, 60, None):
    print(f"bought in [0, {upper}]:")
    print("  ", months_bought(upper))
