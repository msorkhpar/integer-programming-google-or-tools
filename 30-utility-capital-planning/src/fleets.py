"""Lesson 7.1.2: how GridCap's three fleets differ in size, length and kind of work.

GridCap is a fictional utility's portfolio, generated for this course; no number in it is real.
"""

from statistics import median

from gridcap import PROGRAMS, generate

small = generate("small")

print("program        projects  capex min / median / max ($k)  years of work  interventions")
for prog in PROGRAMS:
    mine = [p for p in small.projects if p.program == prog]
    capex = [p.capex for p in mine]
    years = sum(p.duration for p in mine) / len(mine)
    kinds = sorted({p.intervention for p in mine})
    print(f"{prog:14} {len(mine):8}  {min(capex):6,} / {median(capex):6,.0f} / {max(capex):6,}"
          f"         {years:4.1f}         {', '.join(kinds)}")

print()
print("program        crew-months asked  crew-months available 2027-2031")
for prog in PROGRAMS:
    asked = sum(p.crew_months for p in small.projects if p.program == prog)
    have = [small.crews[(prog, y)] for y in small.years]
    print(f"{prog:14} {asked:17}  {have}")

print()
for prog in PROGRAMS:
    p = next(p for p in small.projects if p.program == prog)
    print(f"{prog:14} e.g. {p.project_id} {p.name}: spends {list(p.cost_profile)}, may start {p.earliest_start}-{p.latest_start}")
