from __future__ import annotations

from dataclasses import dataclass

from ortools.sat.python import cp_model


@dataclass(frozen=True)
class Job:
    name: str
    district: str
    value: int      # risk removed, in points
    hours: int      # crew-hours the inspection takes


def build(jobs: list[Job], hours: int) -> tuple[cp_model.CpModel, dict[str, cp_model.IntVar]]:
    """Given: the week's model. pick[j] = 1 runs job j; the crews have `hours` in total."""
    model = cp_model.CpModel()
    pick = {j.name: model.new_bool_var(f"pick_{j.name}") for j in jobs}
    model.add(sum(j.hours * pick[j.name] for j in jobs) <= hours)
    model.maximize(sum(j.value * pick[j.name] for j in jobs))
    return model, pick


def improve(jobs: list[Job], hours: int, plan: set[str], free: set[str]) -> set[str]:
    """The best plan that keeps every job outside `free` exactly as `plan` has it."""
    # TODO: fix every job outside `free` to its value in `plan`, hint the plan, solve with one worker.
    return set()


if __name__ == "__main__":
    week = [Job("N1", "north", 30, 10), Job("N2", "north", 25, 10), Job("N3", "north", 10, 10),
            Job("S1", "south", 50, 20)]
    print(sorted(improve(week, 40, {"N3", "S1"}, {"N1", "N2", "N3"})))
