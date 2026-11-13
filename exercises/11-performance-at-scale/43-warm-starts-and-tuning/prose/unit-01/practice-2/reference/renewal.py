from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt


@dataclass(frozen=True)
class Job:
    name: str
    cost: int                        # $k, all spent in the year the job is done
    value: int                       # $k of benefit, whatever the year
    years: tuple[int, ...]           # the years it may be done in, earliest first
    must: bool = False


def greedy_plan(jobs: list[Job], budget: dict[int, int]) -> dict[str, int]:
    """Must-do jobs first, then the rest by value per $k (ties by name), each in its earliest year that still fits."""
    left = dict(budget)
    plan = {}
    order = sorted(jobs, key=lambda j: (not j.must, -j.value / j.cost, j.name))
    for job in order:
        for year in job.years:
            if job.cost <= left.get(year, 0):
                plan[job.name] = year
                left[year] -= job.cost
                break
    return plan


def as_hint(x: dict[tuple[str, int], mathopt.Variable], plan: dict[str, int]) -> mathopt.SolutionHint:
    """The plan as a complete start: 1 for each (job, year) the plan uses, 0 for every other variable."""
    return mathopt.SolutionHint(variable_values={v: 1.0 if plan.get(name) == year else 0.0
                                                 for (name, year), v in x.items()})


if __name__ == "__main__":
    jobs = [Job("main-st", 300, 900, (2028, 2029), must=True), Job("elm-ave", 200, 500, (2028,))]
    print(greedy_plan(jobs, {2028: 400, 2029: 300}))
