from __future__ import annotations

from ortools.sat.python import cp_model


def shortest_schedule(jobs: dict[str, int], booked: list[tuple[int, int]], horizon: int) -> dict[str, int]:
    """Start day of each job on one rig, so the last job ends as early as possible."""
    model = cp_model.CpModel()
    start, intervals = {}, []
    for name, days in jobs.items():
        start[name] = model.new_int_var(0, horizon - days, f"start_{name}")
        intervals.append(model.new_fixed_size_interval_var(start[name], days, f"work_{name}"))
    for first, last in booked:
        intervals.append(model.new_fixed_size_interval_var(first, last - first + 1, f"booked_{first}"))
    model.add_no_overlap(intervals)

    makespan = model.new_int_var(0, horizon, "makespan")
    model.add_max_equality(makespan, [start[name] + days for name, days in jobs.items()])
    model.minimize(makespan)
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1
    solver.solve(model)
    return {name: solver.value(start[name]) for name in jobs}


if __name__ == "__main__":
    print(shortest_schedule({"S1": 3, "S2": 2, "S3": 4}, [(4, 5)], 20))
