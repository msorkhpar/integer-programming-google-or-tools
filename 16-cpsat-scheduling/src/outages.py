"""Lesson 4.5.2: outage windows as start domains, and one de-energized circuit per region at a time.

The domain idea follows the OR-Tools sample scheduling_with_calendar_sample_sat.py, which gives a
start variable a domain with gaps through Domain.from_intervals,
https://github.com/google/or-tools/blob/stable/ortools/sat/samples/scheduling_with_calendar_sample_sat.py.
GridCap is fictional.
"""

from cpsat_run import solve
from season import OUTAGE_WINDOWS, jobs
from season_model import STANDBY, build, minimize_makespan, show, start_domain, starts

season = jobs()
for j in season:
    if j.needs_outage:
        print(f"{j.jid} {j.region:<6} {j.weeks} weeks  windows {OUTAGE_WINDOWS[j.region]}"
              f"  start in {start_domain(j, 30)}")

for rule, region_rule in (("windows only", False), ("windows, one outage per region", True)):
    s = build(season, standby=STANDBY, outages=True, one_outage_per_region=region_rule)
    minimize_makespan(s)
    solver, status = solve(s.model)
    print(f"{rule}: {status}, makespan {solver.value(s.makespan)} weeks")
    show([j for j in season if j.needs_outage], starts(s, solver))
