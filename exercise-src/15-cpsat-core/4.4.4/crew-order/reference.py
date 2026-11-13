from __future__ import annotations

from dataclasses import dataclass

from ortools.sat.python import cp_model


@dataclass(frozen=True)
class Job:
    name: str
    days: int      # days the job takes
    due: int       # the day it is due (lateness is measured from here)
    weight: int    # cost of one day of lateness


def best_order(jobs: list[Job]) -> tuple[int, list[str]]:
    """The least weighted lateness for one crew doing the jobs one at a time, and the order that gives it."""
    horizon = sum(j.days for j in jobs)
    model = cp_model.CpModel()
    start = {j.name: model.new_int_var(0, horizon, f"start_{j.name}") for j in jobs}
    late = {j.name: model.new_int_var(0, horizon, f"late_{j.name}") for j in jobs}
    for j in jobs:
        model.add(late[j.name] >= start[j.name] + j.days - j.due)
    for a, b in ((a, b) for i, a in enumerate(jobs) for b in jobs[i + 1:]):
        first = model.new_bool_var(f"{a.name}_before_{b.name}")
        model.add(start[a.name] + a.days <= start[b.name]).only_enforce_if(first)
        model.add(start[b.name] + b.days <= start[a.name]).only_enforce_if(~first)
    model.minimize(sum(j.weight * late[j.name] for j in jobs))
    solver = cp_model.CpSolver()
    solver.solve(model)
    order = sorted(start, key=lambda name: solver.value(start[name]))
    return round(solver.objective_value), order


if __name__ == "__main__":
    print(best_order([Job("north", 3, 4, 2), Job("ridge", 2, 2, 5), Job("creek", 4, 6, 1)]))
