"""Lesson 4.5.4: turn the pool schedule into named crews A, B and C.

The cumulative constraint promises that no week needs more crews than there are, not which crew
does what. Handing out crews in order of start week, each job (and the storm standby) taking the
crews that are free, never runs short: a job needing k crews is k copies of one interval, and
intervals can always be coloured with as many colours as the most that overlap at once.
GridCap is fictional.
"""

from cpsat_run import solve
from season import CREWS, jobs
from season_model import STANDBY, build, minimize_lateness, starts

season = jobs()
s = build(season, standby=STANDBY, outages=True, one_outage_per_region=True)
minimize_lateness(s)
solver, status = solve(s.model)
start = starts(s, solver)

work = [(start[j.jid], start[j.jid] + j.weeks, j.crews, j.jid) for j in season]
work += [(first, first + weeks, away, "standby") for first, (weeks, away) in STANDBY.items()]
free_from = {name: 0 for name in "ABC"[:CREWS]}        # crew -> the week it is next free
crew_of = {}
for s_, e, need, what in sorted(work):
    free = sorted(c for c, f in free_from.items() if f <= s_)
    assert len(free) >= need, f"no crews left for {what}"
    crew_of[what] = free[:need]
    for c in free[:need]:
        free_from[c] = e
for c in free_from:
    print(f"crew {c}: " + ", ".join(f"{what} {s_}-{e - 1}" for s_, e, _, what in sorted(work) if c in crew_of[what]))
