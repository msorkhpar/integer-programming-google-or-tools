"""The planner's entry point, a request in and a plan out, and a check of one fixed plan."""

from __future__ import annotations

from dataclasses import dataclass

from ortools.sat.python import cp_model

from .model import Built, build
from .portfolio import Project
from .request import Request

FOUND = (cp_model.OPTIMAL, cp_model.FEASIBLE)


@dataclass
class Plan:
    starts: dict[str, int]       # project id -> the year it starts
    value: int                   # $k
    status: str                  # CP-SAT's name for how the solve ended


def solve(built: Built) -> tuple[cp_model.CpSolver, int]:
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1            # one worker: the same plan on every run
    solver.parameters.max_time_in_seconds = 30
    return solver, solver.solve(built.model)


def plan(projects: list[Project], request: Request) -> Plan:
    """The starts of greatest total value that keep every rule of the request."""
    built = build(projects, request)
    solver, status = solve(built)
    if status not in FOUND:
        return Plan({}, 0, solver.status_name(status))
    starts = {pid: y for (pid, y), var in built.x.items() if solver.value(var)}
    return Plan(dict(sorted(starts.items())), round(solver.objective_value), solver.status_name(status))


def allows(projects: list[Project], request: Request, starts: set[tuple[str, int]]) -> bool:
    """Does the model accept exactly these (project, year) starts, and no other?"""
    built = build(projects, request)
    if any(start not in built.x for start in starts):
        return False                             # no variable: the year is outside the project's window
    for key, var in built.x.items():
        built.model.add(var == (1 if key in starts else 0))
    return solve(built)[1] in FOUND
