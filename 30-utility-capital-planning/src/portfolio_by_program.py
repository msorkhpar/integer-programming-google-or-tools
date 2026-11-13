"""Lesson 7.1.1: what GridCap's candidate portfolio asks for, by program and by region, against its budgets.

GridCap is a fictional utility's portfolio, generated for this course; no number in it is real.
"""

from gridcap import PROGRAMS, REGIONS, generate
from cycle_model import base_scenario, optimize

small = generate("small")

print("program        projects  must-do  requested ($k)  share")
asked = sum(p.capex for p in small.projects)
for prog in PROGRAMS:
    mine = [p for p in small.projects if p.program == prog]
    requested = sum(p.capex for p in mine)
    print(f"{prog:14} {len(mine):8} {sum(p.must_do for p in mine):8} {requested:15,} {requested / asked:6.0%}")
budgets = sum(small.budget.values())
print(f"{'portfolio':14} {len(small.projects):8} {sum(p.must_do for p in small.projects):8} {asked:15,}")
print(f"budgets {min(small.years)}-{max(small.years)}: {budgets:,}  requested / budgets = {asked / budgets:.2f}")

print()
print("region   requested ($k)  floor ($k)")
for r in REGIONS:
    requested = sum(p.capex for p in small.projects if p.region == r)
    print(f"{r:8} {requested:15,} {small.region_floor[r]:11,}")

run = optimize(base_scenario(small))
funded = [small.project(i) for i in run.starts]
print()
print(f"the optimized plan funds {len(funded)} of {len(small.projects)} projects:")
for prog in PROGRAMS:
    got = sum(p.capex for p in funded if p.program == prog)
    print(f"  {prog:14} {got:7,} of {sum(p.capex for p in small.projects if p.program == prog):7,} requested")
