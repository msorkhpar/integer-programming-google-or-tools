"""The season's crew schedule in CP-SAT, built up over lessons 4.5.2 and 4.5.4.

Every job is a fixed-size interval on a start variable. The crew pool is one cumulative constraint;
weeks with fewer crews are fixed intervals that hold the missing crews; outage windows are domains
on the start of each circuit clear, and a region de-energizes one circuit at a time. The objective
is the makespan or the risk-weighted lateness. GridCap is fictional, and so is this season.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ortools.sat.python import cp_model

from season import CREWS, HORIZON, OUTAGE_WINDOWS, Job

STANDBY = {12: (4, 1)}          # from week 12, for 4 weeks, 1 crew is held back for storm duty


@dataclass
class Season:
    model: cp_model.CpModel
    jobs: list[Job]
    start: dict[str, cp_model.IntVar] = field(default_factory=dict)
    task: dict[str, cp_model.IntervalVar] = field(default_factory=dict)
    late: dict[str, cp_model.IntVar] = field(default_factory=dict)
    makespan: cp_model.IntVar | None = None

    def end(self, jid: str):
        return self.task[jid].end_expr()


def start_domain(j: Job, horizon: int) -> cp_model.Domain:
    """Every start that keeps the job inside one of its region's outage windows."""
    return cp_model.Domain.from_intervals(
        [[a, b - j.weeks] for a, b in OUTAGE_WINDOWS[j.region] if b - j.weeks >= a and a < horizon])


def build(jobs: list[Job], *, crews: int = CREWS, horizon: int = HORIZON, standby: dict | None = None,
          outages: bool = False, one_outage_per_region: bool = False) -> Season:
    model = cp_model.CpModel()
    s = Season(model, jobs)
    for j in jobs:
        if outages and j.needs_outage:
            s.start[j.jid] = model.new_int_var_from_domain(start_domain(j, horizon), f"start_{j.jid}")
        else:
            s.start[j.jid] = model.new_int_var(0, horizon - j.weeks, f"start_{j.jid}")
        s.task[j.jid] = model.new_fixed_size_interval_var(s.start[j.jid], j.weeks, f"work_{j.jid}")

    intervals = [s.task[j.jid] for j in jobs]
    demands = [j.crews for j in jobs]
    for first, (weeks, away) in (standby or {}).items():
        intervals.append(model.new_fixed_size_interval_var(first, weeks, f"standby_{first}"))
        demands.append(away)
    model.add_cumulative(intervals, demands, crews)

    if one_outage_per_region:
        for region in OUTAGE_WINDOWS:
            clears = [s.task[j.jid] for j in jobs if j.region == region and j.needs_outage]
            if len(clears) > 1:
                model.add_no_overlap(clears)
    return s


def minimize_makespan(s: Season, horizon: int = HORIZON) -> None:
    s.makespan = s.model.new_int_var(0, horizon, "makespan")
    s.model.add_max_equality(s.makespan, [s.end(j.jid) for j in s.jobs])
    s.model.minimize(s.makespan)


def minimize_lateness(s: Season, horizon: int = HORIZON) -> None:
    """late_j = max(0, end_j - due_j); minimize the sum of weight_j * late_j."""
    for j in s.jobs:
        s.late[j.jid] = s.model.new_int_var(0, horizon, f"late_{j.jid}")
        s.model.add_max_equality(s.late[j.jid], [0, s.end(j.jid) - j.due])
    s.model.minimize(sum(j.weight * s.late[j.jid] for j in s.jobs))


def starts(s: Season, solver: cp_model.CpSolver) -> dict[str, int]:
    return {j.jid: solver.value(s.start[j.jid]) for j in s.jobs}


def crews_per_week(jobs: list[Job], start: dict[str, int], horizon: int = HORIZON) -> list[int]:
    """How many crews the schedule has at work in each week."""
    used = [0] * horizon
    for j in jobs:
        for w in range(start[j.jid], start[j.jid] + j.weeks):
            used[w] += j.crews
    return used


def show(jobs: list[Job], start: dict[str, int]) -> None:
    for j in sorted(jobs, key=lambda j: (start[j.jid], j.jid)):
        s, e = start[j.jid], start[j.jid] + j.weeks
        late = max(0, e - j.due)
        print(f"  {j.jid} {j.region:<6} {j.intervention:<5} crews {j.crews}  weeks {s:>2}-{e - 1:>2}"
              f"  due {j.due:>2}" + (f"  late {late} x {j.weight}" if late else ""))
