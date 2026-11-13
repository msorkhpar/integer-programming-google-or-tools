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
    # TODO: write the rule down first, then fill the plan one job at a time.
    return {}


def as_hint(x: dict[tuple[str, int], mathopt.Variable], plan: dict[str, int]) -> mathopt.SolutionHint:
    """The plan as a complete start: 1 for each (job, year) the plan uses, 0 for every other variable."""
    # TODO: one value for each variable in x.
    return mathopt.SolutionHint()


if __name__ == "__main__":
    jobs = [Job("main-st", 300, 900, (2028, 2029), must=True), Job("elm-ave", 200, 500, (2028,))]
    print(greedy_plan(jobs, {2028: 400, 2029: 300}))
