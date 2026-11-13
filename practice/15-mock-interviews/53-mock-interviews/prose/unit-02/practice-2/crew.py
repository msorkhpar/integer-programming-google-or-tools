from __future__ import annotations

from dataclasses import dataclass

from ortools.sat.python import cp_model


@dataclass(frozen=True)
class Job:
    name: str
    duration: int        # whole weeks; started in week s, it works weeks s .. s + duration - 1
    release: int         # it may not start before this week
    deadline: int        # its end, start + duration, is at most this week


def start_variables(model: cp_model.CpModel, jobs: list[Job], horizon: int) -> dict[str, cp_model.IntVar]:
    """Given: one integer start week per job, from its release to the last start that ends by the horizon."""
    return {j.name: model.new_int_var(j.release, horizon - j.duration, f"start_{j.name}") for j in jobs}


def add_rules(model: cp_model.CpModel, start: dict, jobs: list[Job], blocked: list[tuple[int, int]]) -> None:
    """One crew: no two jobs at once, no work in a blocked period (first, last week), every deadline met."""
    # TODO: the crew's intervals, the blocked periods and the deadlines.
    return None


def build(jobs: list[Job], blocked: list[tuple[int, int]], horizon: int) -> tuple[cp_model.CpModel, dict]:
    model = cp_model.CpModel()
    start = start_variables(model, jobs, horizon)
    add_rules(model, start, jobs, blocked)
    model.minimize(sum(start[j.name] + j.duration for j in jobs))
    return model, start


if __name__ == "__main__":
    model, start = build([Job("A", 2, 0, 6), Job("B", 1, 0, 6)], [(2, 3)], 10)
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1
    print(solver.status_name(solver.solve(model)), {n: solver.value(v) for n, v in start.items()})
