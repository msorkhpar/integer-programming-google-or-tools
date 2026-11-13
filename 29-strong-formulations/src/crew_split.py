"""Splitting a region's transmission jobs among identical line crews: a model full of symmetry.

Each job goes to one crew; a crew works its jobs one after another, so its load (crew-months) is
the month it finishes. The plan finishes when the busiest crew does: minimize that makespan. The
crews are identical (same skills, same depot), so renumbering them gives the same plan.

The scenario reads GridCap medium's `crew_months` as the months one crew needs for a job; that
reading, and the crew counts, are this module's own. GridCap is fictional.
"""

from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt
from ortools.math_opt.solvers import highs_pb2

from gridcap import Portfolio
from strong_model import solve_highs


@dataclass
class CrewSplit:
    model: mathopt.Model
    x: dict[tuple[str, int], mathopt.Variable]          # x[j, k] = 1: job j goes to crew k
    makespan: mathopt.Variable
    jobs: dict[str, int]                                  # job -> crew-months, largest first


def region_jobs(portfolio: Portfolio, region: str, count: int = 14) -> dict[str, int]:
    """The region's `count` largest transmission jobs by crew-months, largest first (ties by id)."""
    jobs = [p for p in portfolio.projects if p.region == region and p.program == "transmission"]
    jobs.sort(key=lambda p: (-p.crew_months, p.project_id))
    return {p.project_id: p.crew_months for p in jobs[:count]}


def build(jobs: dict[str, int], crews: int, order: str | None = None) -> CrewSplit:
    model = mathopt.Model(name="crew split")
    x = {(j, k): model.add_binary_variable(name=f"x_{j}_{k}") for j in jobs for k in range(crews)}
    makespan = model.add_variable(lb=0, ub=sum(jobs.values()), name="makespan")
    for j in jobs:
        model.add_linear_constraint(sum(x[j, k] for k in range(crews)) == 1, name=f"one_crew_{j}")
    load = [sum(m * x[j, k] for j, m in jobs.items()) for k in range(crews)]
    for k in range(crews):
        model.add_linear_constraint(load[k] <= makespan, name=f"finish_{k}")
    add_order(model, x, jobs, crews, load, order)
    model.minimize(makespan)
    return CrewSplit(model, x, makespan, jobs)


def add_order(model, x, jobs, crews, load, order: str | None) -> None:
    """Rows that keep one numbering of the crews out of the many that describe the same plan."""
    if order is None:
        return
    if order == "load":
        # Crew 0 is the busiest, crew 1 the next, and so on.
        for k in range(crews - 1):
            model.add_linear_constraint(load[k] >= load[k + 1], name=f"load_order_{k}")
    elif order == "index":
        # Job number n (0-based, in the jobs' order) may only go to crews 0..n.
        for n, j in enumerate(jobs):
            for k in range(n + 1, crews):
                model.add_linear_constraint(x[j, k] == 0, name=f"index_order_{j}_{k}")
    else:
        raise ValueError(order)


def params(detect: bool) -> mathopt.SolveParameters:
    """An exact solve, with HiGHS's own symmetry detection on (its default) or off."""
    return mathopt.SolveParameters(
        relative_gap_tolerance=0.0,
        highs=highs_pb2.HighsOptionsProto(bool_options={"mip_detect_symmetry": detect}))


def solve(cs: CrewSplit, detect: bool = True) -> mathopt.SolveResult:
    return solve_highs(cs.model, params(detect))


def assignment(cs: CrewSplit, result: mathopt.SolveResult) -> list[list[str]]:
    """The jobs of each crew, crew 0 first."""
    crews = 1 + max(k for _, k in cs.x)
    return [[j for j in cs.jobs if result.variable_values(cs.x[j, k]) > 0.5] for k in range(crews)]


@dataclass
class CrewCounts:
    model: mathopt.Model
    n: dict[tuple[int, int], mathopt.Variable]          # n[s, k]: how many jobs of s crew-months crew k gets
    makespan: mathopt.Variable


def build_counts(jobs: dict[str, int], crews: int, order: str | None = None) -> CrewCounts:
    """Jobs of equal length are interchangeable too: count them per length instead of naming them."""
    model = mathopt.Model(name="crew split, counted")
    lengths = sorted(set(jobs.values()), reverse=True)
    have = {s: sum(1 for m in jobs.values() if m == s) for s in lengths}
    n = {(s, k): model.add_integer_variable(lb=0, ub=have[s], name=f"n_{s}_{k}") for s in lengths for k in range(crews)}
    makespan = model.add_variable(lb=0, ub=sum(jobs.values()), name="makespan")
    for s in lengths:
        model.add_linear_constraint(sum(n[s, k] for k in range(crews)) == have[s], name=f"all_{s}")
    load = [sum(s * n[s, k] for s in lengths) for k in range(crews)]
    for k in range(crews):
        model.add_linear_constraint(load[k] <= makespan, name=f"finish_{k}")
    if order == "load":
        for k in range(crews - 1):
            model.add_linear_constraint(load[k] >= load[k + 1], name=f"load_order_{k}")
    model.minimize(makespan)
    return CrewCounts(model, n, makespan)
