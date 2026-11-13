"""Lesson 2.3.3: ask HiGHS itself for the ranges, then check two of them by re-solving with MathOpt."""

import math

import highspy
from ortools.math_opt.python import mathopt

from budget_lp import build, clean, solve_glop
from gridcap import generate


def to_highs(model: mathopt.Model) -> highspy.Highs:
    """The same LP, handed to HiGHS through its own Python API (MathOpt has no ranging call)."""
    h = highspy.Highs()
    h.setOptionValue("output_flag", False)
    inf = highspy.kHighsInf
    column = {}
    for var in model.variables():                                  # columns in MathOpt's order
        column[var] = h.addVariable(lb=max(var.lower_bound, -inf), ub=min(var.upper_bound, inf), name=var.name)
    for row in model.linear_constraints():                         # rows in MathOpt's order
        terms = list(row.terms())
        h.addRow(max(row.lower_bound, -inf), min(row.upper_bound, inf), len(terms),
                 [column[t.variable].index for t in terms], [t.coefficient for t in terms])
    objective = sum(t.coefficient * column[t.variable] for t in model.objective.linear_terms())
    if model.objective.is_maximize:
        h.maximize(objective)                                      # sets the objective and solves
    else:
        h.minimize(objective)
    return h


tiny = generate("tiny")
lp = build(tiny)
h = to_highs(lp.model)
print("HiGHS", h.getModelStatus().name, f"value {h.getInfo().objective_function_value:,.1f}")
status, ranging = h.getRanging()
rows = list(lp.model.linear_constraints())
variables = list(lp.model.variables())

print(f"{'binding row':14} {'rhs':>6} {'price':>7} {'price holds from':>17} {'to':>6}")
for row in (*lp.cash.values(), lp.floor):
    i = rows.index(row)
    rhs = row.upper_bound if row.upper_bound < math.inf else row.lower_bound
    price = h.getSolution().row_dual[i]
    print(f"{row.name:14} {rhs:>6,.0f} {clean(price):>7} {ranging.row_bound_dn.value_[i]:>17,.0f} "
          f"{ranging.row_bound_up.value_[i]:>6,.0f}")

print(f"{'variable':24} {'coefficient':>11} {'plan holds from':>16} {'to':>7}")
for key in (("transmission", 2028), ("vegetation", 2027), ("vegetation", 2029)):
    var = lp.spend[key]
    j = variables.index(var)
    print(f"{var.name:24} {lp.model.objective.get_linear_coefficient(var):>11.4f} "
          f"{ranging.col_cost_dn.value_[j]:>16.4f} {ranging.col_cost_up.value_[j]:>7.4f}")

# Check the cash_2028 range by re-solving 10 below and 10 above each end.
for b in (2970, 2990, 8130, 8150):
    lp28 = build(tiny, budget={**tiny.budget, 2028: b})
    print(f"re-solve, 2028 budget {b:,}: price {clean(solve_glop(lp28.model).dual_values(lp28.cash[2028]))}")

# Why spend_vegetation_2027's cost range starts at -inf: the floor pins it, whatever it is worth.
veg = {y: lp.crew["vegetation", y].upper_bound for y in tiny.years}
print("vegetation crew limits: " + ", ".join(f"{y} {cap:,.0f}" for y, cap in veg.items())
      + f"; floor {lp.floor.lower_bound:,.0f} - {veg[2028]:,.0f} - {veg[2029]:,.0f} = "
      f"{lp.floor.lower_bound - veg[2028] - veg[2029]:,.0f} must come from 2027")
for coefficient in (0.31, -1.0, -100.0):
    lp_low = build(tiny)
    lp_low.model.objective.set_linear_coefficient(lp_low.spend["vegetation", 2027], coefficient)
    low = solve_glop(lp_low.model)
    plan = ", ".join(f"{y} {low.variable_values(lp_low.spend['vegetation', y]):,.1f}" for y in tiny.years)
    print(f"vegetation 2027 worth {coefficient:7.2f}: vegetation spend {plan}; "
          f"floor price {clean(low.dual_values(lp_low.floor))}")
