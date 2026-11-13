"""Lesson 5.1.1: the Pyomo port of lesson 6.4.1's multi-period model, solved on GridCap small.

GridCap is a fictional utility's portfolio. Lesson 6.4.1 solved the same model in MathOpt and
printed NPV $24,260k with 27 of 40 projects started; this program prints the Pyomo model's answer
in the same form, so the two can be compared line by line.
"""

import pyomo.environ as pyo

from gridcap import generate
from pyomo_timing import build, highs, schedule

small = generate("small")
m = build(small)
print(f"{len(m.x)} variables, {m.nconstraints()} rows:",
      {c.local_name: len(c) for c in m.component_objects(pyo.Constraint)})
highs().solve(m)
plan = schedule(m)
print(f"NPV ${pyo.value(m.value):,.0f}k")
late = {pid: t for pid, t in plan.items() if t > small.project(pid).earliest_start}
print(f"started {len(plan)} of {len(small.projects)}; {len(late)} later than their earliest year")
by_year = {y: sum(1 for t in plan.values() if t == y) for y in small.years}
print("starts per year:", by_year)
