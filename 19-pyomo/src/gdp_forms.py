"""Lesson 5.1.3: one GDP statement of the outage disjunctions, turned into big-M rows and into the hull by Pyomo.

GridCap is a fictional utility's portfolio. Lesson 6.2.4 wrote both forms by hand in MathOpt
for the three Coast jobs P011, P016 and P021 (LP bounds 10.00 and 13.98, MILP 17). Here
`gdp.bigm` and `gdp.hull` write them from the same disjunctions; each form is solved as a MILP
and, after `core.relax_integer_vars`, as its LP relaxation.
"""

import pyomo.environ as pyo

from gridcap import generate
from outage_gdp import build, first
from pyomo_timing import highs

small = generate("small")
durations = {pid: small.project(pid).crew_months for pid in ("P011", "P016", "P021")}
HORIZON = 12

m = build(durations, HORIZON)
m.order.pprint()

for form in ("gdp.bigm", "gdp.hull"):
    milp = build(durations, HORIZON)
    pyo.TransformationFactory(form).apply_to(milp)
    binaries = sum(1 for v in milp.component_data_objects(pyo.Var) if v.is_binary())
    size = f"{milp.nvariables()} variables ({binaries} binary), {milp.nconstraints()} rows"
    highs().solve(milp)
    best = pyo.value(milp.finish)
    pyo.TransformationFactory("core.relax_integer_vars").apply_to(milp)
    highs().solve(milp)
    print(f"{form:9} {size}  LP bound {pyo.value(milp.finish):.2f}  MILP {best:.1f}")

# The wrong order: relaxing first finds no binary yet, so the transformation's binaries stay binary.
early = build(durations, HORIZON)
pyo.TransformationFactory("core.relax_integer_vars").apply_to(early)
pyo.TransformationFactory("gdp.hull").apply_to(early)
highs().solve(early)
print(f"relax, then gdp.hull: 'LP bound' {pyo.value(early.finish):.2f}")

milp = build(durations, HORIZON)
bigm = pyo.TransformationFactory("gdp.bigm")
bigm.apply_to(milp)
Ms = bigm.get_all_M_values_by_constraint(milp)
print(f"(lower M, upper M) of the {len(Ms)} disjunct rows:", set(Ms.values()))
row = milp.order["P011", "P016"].disjuncts[0].constraint[1]
print("P011 before P016 becomes:", bigm.get_transformed_constraints(row)[0].expr)
highs().solve(milp)
print(f"MILP {pyo.value(milp.finish):.1f}  starts {[round(milp.s[j].value, 2) for j in milp.J]}  first {first(milp)}")
