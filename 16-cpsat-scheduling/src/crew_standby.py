"""Lesson 4.5.2: one crew held back for storm duty in weeks 12-15, as a fixed interval that
takes one unit of the pool's capacity.

The idea is the OR-Tools sample cumulative_variable_profile_sample_sat.py, which lowers a
cumulative's capacity in some periods with fixed intervals,
https://github.com/google/or-tools/blob/stable/ortools/sat/samples/cumulative_variable_profile_sample_sat.py.
GridCap is fictional.
"""

from cpsat_run import solve
from season import jobs
from season_model import STANDBY, build, crews_per_week, minimize_makespan, show, starts

season = jobs()
s = build(season, standby=STANDBY)
minimize_makespan(s)
solver, status = solve(s.model)
print(f"{status}: makespan {solver.value(s.makespan)} weeks")
start = starts(s, solver)
show(season, start)
print("crews at work by week:", "".join(str(n) for n in crews_per_week(season, start)))
print("crews available:      ", "".join("2" if 12 <= w < 16 else "3" for w in range(len(crews_per_week(season, start)))))
