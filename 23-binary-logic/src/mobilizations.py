"""Lesson 6.1.1: a count rounded up to whole batches needs an integer variable.

GridCap is a fictional utility's portfolio. Its (fictional) vegetation contractor bills a $90k
mobilization for every batch of up to three vegetation projects, paid from the capital budget.
"""

import math

from gridcap import generate
from selection_model import EXACT, build, funded, ids, solve_highs

small = generate("small")
vegetation = ids(small, program="vegetation")
FEE, BATCH = 90, 3


def plan_with_mobilizations(integer: bool):
    sel = build(small)
    m = sel.model.add_variable(lb=0, is_integer=integer, name="mobilizations")
    sel.model.add_linear_constraint(BATCH * m >= sum(sel.x[i] for i in vegetation), name="batches")
    sel.budget.set_coefficient(m, FEE)          # the budget row now reads capex + 90 m <= B
    result = solve_highs(sel.model, EXACT)
    return result, sel, m


for integer in (True, False):
    result, sel, m = plan_with_mobilizations(integer)
    chosen = [i for i in funded(sel, result) if i in vegetation]
    spent = sum(small.project(i).capex for i in funded(sel, result)) + FEE * result.variable_values(m)
    print(f"m {'integer' if integer else 'continuous'}: NPV ${result.objective_value():,.0f}k, "
          f"{len(chosen)} vegetation projects, m = {result.variable_values(m):.4g}, spend ${spent:,.0f}k")
    print(f"  vegetation funded: {chosen}")
    if not integer:
        billed = math.ceil(len(chosen) / BATCH)
        real = spent - FEE * result.variable_values(m) + FEE * billed
        print(f"  the contractor bills {billed} whole mobilizations: spend ${real:,.0f}k, "
              f"${real - small.capital_budget:,.0f}k over budget")
