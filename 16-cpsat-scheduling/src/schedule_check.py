"""Lesson 4.5.4: check a season schedule against every rule without the solver.

A checker written straight from the rules, in plain Python, is how a test proves that the model
says what the planners said. GridCap is fictional.
"""

from __future__ import annotations

from season import CREWS, HORIZON, OUTAGE_WINDOWS, Job
from season_model import STANDBY


def violations(jobs: list[Job], start: dict[str, int], standby: dict = STANDBY) -> list[str]:
    found = []
    for j in jobs:
        s, e = start[j.jid], start[j.jid] + j.weeks
        if s < 0 or e > HORIZON:
            found.append(f"{j.jid} runs outside the season (weeks {s}-{e - 1})")
        if j.needs_outage and not any(a <= s and e <= b for a, b in OUTAGE_WINDOWS[j.region]):
            found.append(f"{j.jid} is not inside one {j.region} outage window (weeks {s}-{e - 1})")
    for w in range(HORIZON):
        away = sum(n for first, (weeks, n) in standby.items() if first <= w < first + weeks)
        busy = sum(j.crews for j in jobs if start[j.jid] <= w < start[j.jid] + j.weeks)
        if busy > CREWS - away:
            found.append(f"week {w}: {busy} crews at work, {CREWS - away} available")
    clears = [j for j in jobs if j.needs_outage]
    for a in clears:
        for b in clears:
            if a.jid < b.jid and a.region == b.region and \
                    start[a.jid] < start[b.jid] + b.weeks and start[b.jid] < start[a.jid] + a.weeks:
                found.append(f"{a.jid} and {b.jid} de-energize {a.region} circuits at the same time")
    return found


def risk(jobs: list[Job], start: dict[str, int]) -> int:
    """The schedule's risk-weighted lateness: sum of weight x weeks late, in $k."""
    return sum(j.weight * max(0, start[j.jid] + j.weeks - j.due) for j in jobs)
