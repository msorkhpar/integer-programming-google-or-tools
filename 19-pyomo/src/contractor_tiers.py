"""Lesson 5.1.4: what Pyomo's Piecewise writes for each constraint type, representation and curve shape.

GridCap is a fictional utility's portfolio. The contractor model (contractor_model.py) is solved
with GridCap's own crews covering 40 transmission crew-months, once per setting. Each line shows
what the Piecewise component added to the model (variables, binaries, rows) and the plan's answer,
next to the contract cost read off the curve by hand at the months bought.
"""

import pyomo.environ as pyo

from contractor_model import COST, DISCOUNT, build, tier_cost
from gridcap import generate
from pyomo_timing import highs

small = generate("small")
OWN = 40


def size(block):
    variables = list(block.component_data_objects(pyo.Var))
    binaries = sum(1 for v in variables if v.is_binary())
    rows = sum(1 for _ in block.component_data_objects(pyo.Constraint, active=True))
    return f"+{len(variables)} vars ({binaries} binary), +{rows} rows"


cases = [
    ("rising tiers, LB, SOS2 (default)", dict(cost=COST, constr_type="LB", repn="SOS2")),
    ("rising tiers, LB, SOS2, force_pw", dict(cost=COST, constr_type="LB", repn="SOS2", force_pw=True)),
    ("rising tiers, LB, INC, force_pw", dict(cost=COST, constr_type="LB", repn="INC", force_pw=True)),
    ("rising tiers, EQ, INC", dict(cost=COST, constr_type="EQ", repn="INC")),
    ("discount, LB, SOS2 (default)", dict(cost=DISCOUNT, constr_type="LB", repn="SOS2")),
    ("discount, LB, INC", dict(cost=DISCOUNT, constr_type="LB", repn="INC")),
    ("discount, UB, INC", dict(cost=DISCOUNT, constr_type="UB", repn="INC")),
]
for label, kwargs in cases:
    m = build(small, OWN, **kwargs)
    added = size(m.tiers)
    try:
        highs().solve(m)
    except NotImplementedError as error:
        print(f"{label:34} {added:30} {type(error).__name__}: {error}")
        continue
    curve = tier_cost(m.bought.value, kwargs["cost"])
    print(f"{label:34} {added:30} net {pyo.value(m.net):9,.1f}  bought {m.bought.value:4.1f}"
          f"  contract {m.contract.value:7.1f}  curve {curve:7.1f}")

# The rows Pyomo wrote for the default case: one line per tier, no binaries.
m = build(small, OWN, cost=COST, constr_type="LB", repn="SOS2")
for row in m.tiers.component_data_objects(pyo.Constraint, active=True):
    print(f"{row.name}: {row.expr}")
