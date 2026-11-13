"""Lesson 5.1.2: duals in Pyomo. They come back for an LP, not for a MILP, and the fixed-integer re-solve is yours to write.

GridCap is a fictional utility's portfolio. A `dual` Suffix asks the solver interface to import
the dual value of every row. The LP relaxation of the timing model has them; the MILP does not;
fixing the binaries at the MILP plan, relaxing them and re-solving gives the LP that has duals for
that plan. On the timing model nothing is left to price once the binaries are fixed; on the
contractor model (contractor_model.py) the crew row gets the price of a contractor month.
"""

import pyomo.environ as pyo

import contractor_model
from gridcap import generate
from pyomo_timing import build, highs

small = generate("small")


def budget_duals(m):
    return {y: round(m.dual[m.spend_cap[y]], 3) for y in m.Y}


# The LP relaxation: x in [0, 1]. Each dual is what one more $k of that year's budget adds to the LP's NPV.
lp = build(small, integer=False)
lp.dual = pyo.Suffix(direction=pyo.Suffix.IMPORT)
highs().solve(lp)
print(f"LP relaxation   NPV {pyo.value(lp.value):,.1f}  budget duals {budget_duals(lp)}")

# The MILP: the same Suffix makes the solve fail when Pyomo asks HiGHS for duals.
milp = build(small)
milp.dual = pyo.Suffix(direction=pyo.Suffix.IMPORT)
try:
    highs().solve(milp)
except RuntimeError as error:
    print("MILP with a dual Suffix:", type(error).__name__, str(error).splitlines()[0])

# The fixed-integer re-solve: solve the MILP, fix every binary at its value, relax integrality, solve the LP.
milp = build(small)
highs().solve(milp)
for v in milp.x.values():
    v.fix(round(v.value))
pyo.TransformationFactory("core.relax_integer_vars").apply_to(milp)
milp.dual = pyo.Suffix(direction=pyo.Suffix.IMPORT)
highs().solve(milp)
print(f"fixed plan, LP  NPV {pyo.value(milp.value):,.1f}  budget duals {budget_duals(milp)}")

# A model with continuous variables left after the fix: contractor crew-months (lesson 5.1.4's model).
c = contractor_model.build(small, own=40)
highs().solve(c)
for v in c.x.values():
    v.fix(round(v.value))
pyo.TransformationFactory("core.relax_integer_vars").apply_to(c)
c.dual = pyo.Suffix(direction=pyo.Suffix.IMPORT)
highs().solve(c)
print(f"contractors     bought {c.bought.value:g} months for ${c.contract.value:,.0f}k;"
      f" crews dual {c.dual[c.crews]:g}, budget dual {c.dual[c.budget]:g}")
