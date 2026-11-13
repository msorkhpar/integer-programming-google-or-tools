from __future__ import annotations

from ortools.sat.python import cp_model


def holiday_plan(jobs: dict[str, tuple[int, int]], available: list[int]) -> dict[str, int]:
    """Start day of each job under a pool that changes by day, so the last ends as early as possible."""
    horizon, peak = len(available), max(available)
    model = cp_model.CpModel()
    start, intervals, demands = {}, [], []
    for name, (days, need) in jobs.items():
        start[name] = model.new_int_var(0, horizon - days, f"start_{name}")
        intervals.append(model.new_fixed_size_interval_var(start[name], days, f"pave_{name}"))
        demands.append(need)
    first = 0
    for t in range(1, horizon + 1):
        if t == horizon or available[t] != available[first]:
            if available[first] < peak:
                intervals.append(model.new_fixed_size_interval_var(first, t - first, f"away_{first}"))
                demands.append(peak - available[first])
            first = t
    model.add_cumulative(intervals, demands, peak)

    makespan = model.new_int_var(0, horizon, "makespan")
    model.add_max_equality(makespan, [start[name] + days for name, (days, _) in jobs.items()])
    model.minimize(makespan)
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1
    solver.solve(model)
    return {name: solver.value(start[name]) for name in jobs}


if __name__ == "__main__":
    print(holiday_plan({"elm": (3, 2), "oak": (2, 1), "ash": (4, 1)}, [3, 3, 1, 1, 3, 3, 3, 3, 3, 3, 3, 3]))
