"""Lesson 4.5.2: the season's twelve jobs on a pool of three crews, with one cumulative constraint.

GridCap is fictional, and so is this season (see season.py).
"""

from math import ceil

from cpsat_run import solve
from season import CREWS, jobs
from season_model import build, crews_per_week, minimize_makespan, show, starts

season = jobs()
crew_weeks = sum(j.weeks * j.crews for j in season)
print(f"{len(season)} jobs, {crew_weeks} crew-weeks of work, {CREWS} crews: "
      f"no schedule ends before week {ceil(crew_weeks / CREWS)}")

s = build(season)
minimize_makespan(s)
solver, status = solve(s.model)
print(f"{status}: makespan {solver.value(s.makespan)} weeks")
start = starts(s, solver)
show(season, start)
print("crews at work by week:", "".join(str(n) for n in crews_per_week(season, start)))
