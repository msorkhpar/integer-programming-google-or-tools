"""The outage layer of lesson 11.3.3: each project's outage job, and one region's year as CP-SAT.

GridCap is fictional, and so is this layer. A transmission or distribution project needs its
equipment switched out of service while the work is done: an outage job of `weeks` weeks (3 plus its crew-months) in the
year it starts, inside a season when the network can spare it. Each region has one outage crew,
and GridCap has one outage crew for the whole network, so the jobs of one year must not overlap. Vegetation work needs no outage.
"""

from __future__ import annotations

from dataclasses import dataclass

from ortools.sat.python import cp_model

from gridcap import Portfolio, Project

#: season name -> (first week, week after the last), in a 52-week year
SEASONS = {"spring": (10, 20), "autumn": (34, 44), "any": (0, 52)}


@dataclass(frozen=True)
class Job:
    project_id: str
    weeks: int
    release: int          # earliest week the outage may begin
    deadline: int         # the outage must end by this week


def job(p: Project) -> Job | None:
    """The outage job of a project, or None for vegetation work."""
    if p.program == "vegetation":
        return None
    number = int(p.project_id[1:])
    weeks = 3 + p.crew_months
    season = ("spring", "autumn", "any")[number % 3]
    first, last = SEASONS[season]
    if weeks > last - first:              # a job longer than its season may run at any time
        first, last = SEASONS["any"]
    return Job(p.project_id, weeks, first, last)


def jobs(portfolio: Portfolio) -> dict[str, Job]:
    return {p.project_id: j for p in portfolio.projects if (j := job(p))}


def schedulable(chosen: list[Job]) -> bool:
    """Can one crew do all these outages in one year, each inside its season, never two at once?"""
    model = cp_model.CpModel()
    intervals = []
    for j in chosen:
        start = model.new_int_var(j.release, j.deadline - j.weeks, f"start_{j.project_id}")
        intervals.append(model.new_fixed_size_interval_var(start, j.weeks, f"outage_{j.project_id}"))
    model.add_no_overlap(intervals)
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1
    return solver.solve(model) in (cp_model.OPTIMAL, cp_model.FEASIBLE)


def minimal_conflict(chosen: list[Job]) -> list[Job]:
    """A deletion filter: drop each job in turn and keep it dropped if the rest still cannot fit."""
    core = list(chosen)
    for j in list(chosen):
        rest = [k for k in core if k is not j]
        if not schedulable(rest):
            core = rest
    return core
