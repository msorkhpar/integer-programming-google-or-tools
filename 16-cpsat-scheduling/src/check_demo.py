"""Lesson 4.5.4: the checker on the solver's schedule and on two hand edits of it.

GridCap is fictional, and so is this season (see season.py).
"""

from cpsat_run import solve
from schedule_check import risk, violations
from season import jobs
from season_model import STANDBY, build, minimize_lateness, starts

season = jobs()
s = build(season, standby=STANDBY, outages=True, one_outage_per_region=True)
minimize_lateness(s)
solver, status = solve(s.model)
best = starts(s, solver)
print(f"solver's schedule: risk ${risk(season, best)}k, rules broken: {violations(season, best) or 'none'}")

edited = {**best, "P015": 9}                 # weeks 9-10: past the end of the Coast window [0, 10)
print(f"P015 moved to week 9: risk ${risk(season, edited)}k")
for problem in violations(season, edited):
    print("  ", problem)

edited = {**best, "P003": 8}                 # earlier, on top of P010 and into a full week
print(f"P003 moved to week 8: risk ${risk(season, edited)}k")
for problem in violations(season, edited):
    print("  ", problem)
