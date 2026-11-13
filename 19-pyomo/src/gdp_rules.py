"""Lesson 5.1.3: what the GDP transformations need (bounds), and planner rules on the disjuncts' Booleans.

GridCap is a fictional utility's portfolio; the jobs are lesson 6.2.4's three Coast outage jobs.
"""

import pyomo.environ as pyo
from pyomo.gdp import GDP_Error

from gridcap import generate
from outage_gdp import build, first
from pyomo_timing import highs

small = generate("small")
durations = {pid: small.project(pid).crew_months for pid in ("P011", "P016", "P021")}

# Remove one upper bound: neither transformation can do its job any more.
for form in ("gdp.bigm", "gdp.hull"):
    m = build(durations, 12)
    m.s["P011"].setub(None)
    try:
        pyo.TransformationFactory(form).apply_to(m)
    except GDP_Error as error:
        print(f"{form}: GDP_Error: {str(error).splitlines()[0]}")

# bigM= supplies M by hand; it must still be valid, which with s[P011] unbounded nothing proves.
m = build(durations, 12)
m.s["P011"].setub(None)
pyo.TransformationFactory("gdp.bigm").apply_to(m, bigM=20)
highs().solve(m)
print(f"bigM=20: MILP {pyo.value(m.finish):.1f}")


def solve(m):
    pyo.TransformationFactory("gdp.bigm").apply_to(m)
    highs().solve(m)
    return f"{round(pyo.value(m.finish), 3):g}  starts {[round(m.s[j].value, 3) + 0.0 for j in m.J]}  first {first(m)}"


# A planner fixes one choice: P021 goes before P011.
m = build(durations, 12)
m.order["P011", "P021"].disjuncts[1].indicator_var.fix(True)
print("P021 before P011:          ", solve(m))

# A logical rule between choices: if P021 goes before P011, it goes before P016 too.
m = build(durations, 12)
m.order["P011", "P021"].disjuncts[1].indicator_var.fix(True)
before_011 = m.order["P011", "P021"].disjuncts[1].indicator_var
before_016 = m.order["P016", "P021"].disjuncts[1].indicator_var
m.lead = pyo.LogicalConstraint(expr=before_011.implies(before_016))
print("... and then before P016:  ", solve(m))
