"""Lesson 4.5.4: the season's schedule that minimizes risk-weighted lateness, every rule on.

GridCap is fictional, and so is this season (see season.py).
"""

from cpsat_run import solve
from schedule_check import risk, violations
from season import jobs
from season_model import STANDBY, build, minimize_lateness, minimize_makespan, show, starts

season = jobs()
RULES = dict(standby=STANDBY, outages=True, one_outage_per_region=True)

hard = build(season, **RULES)
for j in season:
    hard.model.add(hard.end(j.jid) <= j.due)
print("every due week as a hard rule:", solve(hard.model)[1])

fast = build(season, **RULES)
minimize_makespan(fast)
solver, status = solve(fast.model)
quick = starts(fast, solver)
print(f"shortest season: {status}, makespan {solver.value(fast.makespan)}, "
      f"risk-weighted lateness ${risk(season, quick)}k")

s = build(season, **RULES)
minimize_lateness(s)
solver, status = solve(s.model)
best = starts(s, solver)
print(f"least risk: {status}, risk-weighted lateness ${solver.objective_value:.0f}k, "
      f"makespan {max(best[j.jid] + j.weeks for j in season)}")
show(season, best)
print("rules broken:", violations(season, best) or "none")
