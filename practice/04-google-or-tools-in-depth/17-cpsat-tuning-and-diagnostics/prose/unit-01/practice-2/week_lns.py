from __future__ import annotations

from dataclasses import dataclass

from ortools.sat.python import cp_model


@dataclass(frozen=True)
class Job:
    name: str
    district: str
    value: int      # risk points removed
    hours: int      # crew-hours


def build(jobs: list[Job], hours: int) -> tuple[cp_model.CpModel, dict[str, cp_model.IntVar]]:
    """Given: the week's model. pick[j] = 1 runs job j; the crews have `hours` in total."""
    model = cp_model.CpModel()
    pick = {j.name: model.new_bool_var(f"pick_{j.name}") for j in jobs}
    model.add(sum(j.hours * pick[j.name] for j in jobs) <= hours)
    model.maximize(sum(j.value * pick[j.name] for j in jobs))
    return model, pick


def improve(jobs: list[Job], hours: int, plan: set[str], free: set[str]) -> set[str]:
    """Given: one LNS step, the best plan that keeps every job outside `free` as `plan` has it."""
    model, pick = build(jobs, hours)
    for name, var in pick.items():
        model.add_hint(var, 1 if name in plan else 0)
        if name not in free:
            model.add(var == (1 if name in plan else 0))
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1
    solver.solve(model)
    return {name for name, var in pick.items() if solver.value(var)}


def value(jobs: list[Job], plan: set[str]) -> int:
    return sum(j.value for j in jobs if j.name in plan)


def lns(jobs: list[Job], hours: int, start: set[str], rounds: list[set[str]]) -> tuple[set[str], list[int]]:
    """Run one step per neighborhood in `rounds`. Return the final plan and the value after each round."""
    # TODO: one improve() per neighborhood, keeping the better plan each time.
    return set(), [0] * (len(rounds) + 1)


if __name__ == "__main__":
    week = [Job("N1", "north", 50, 20), Job("N3", "north", 30, 15), Job("S3", "south", 20, 5)]
    print(lns(week, 30, {"N3", "S3"}, [{"N1", "N3"}]))
