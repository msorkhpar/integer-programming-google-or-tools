from __future__ import annotations

from ortools.sat.python import cp_model


def possession_plan(jobs: dict[str, tuple[str, int]], possessions: dict[str, list[tuple[int, int]]]) -> dict[str, int]:
    """Start day of each job, inside one possession of its line, so the last ends as early as possible."""
    horizon = max(last + 1 for spans in possessions.values() for _, last in spans)
    model = cp_model.CpModel()
    start, on_line = {}, {}
    for name, (line, days) in jobs.items():
        ranges = [[first, last - days + 1] for first, last in possessions[line] if last - days + 1 >= first]
        start[name] = model.new_int_var_from_domain(cp_model.Domain.from_intervals(ranges), f"start_{name}")
        on_line.setdefault(line, []).append(model.new_fixed_size_interval_var(start[name], days, f"work_{name}"))
    for intervals in on_line.values():
        model.add_no_overlap(intervals)

    makespan = model.new_int_var(0, horizon, "makespan")
    model.add_max_equality(makespan, [start[name] + days for name, (_, days) in jobs.items()])
    model.minimize(makespan)
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1
    solver.solve(model)
    return {name: solver.value(start[name]) for name in jobs}


if __name__ == "__main__":
    print(possession_plan({"rails": ("north", 3), "points": ("north", 2), "drain": ("south", 4)},
                          {"north": [(0, 3), (8, 12)], "south": [(2, 9)]}))
