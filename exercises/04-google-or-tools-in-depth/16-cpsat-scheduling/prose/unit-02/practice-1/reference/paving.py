from __future__ import annotations

from ortools.sat.python import cp_model


def paving_plan(jobs: dict[str, tuple[int, int]], gangs: int, horizon: int) -> dict[str, int]:
    """Start day of each job, so the last ends as early as possible; {} if no plan exists."""
    model = cp_model.CpModel()
    start, intervals, demands = {}, [], []
    for name, (days, need) in jobs.items():
        start[name] = model.new_int_var(0, horizon - days, f"start_{name}")
        intervals.append(model.new_fixed_size_interval_var(start[name], days, f"pave_{name}"))
        demands.append(need)
    model.add_cumulative(intervals, demands, gangs)

    makespan = model.new_int_var(0, horizon, "makespan")
    model.add_max_equality(makespan, [start[name] + days for name, (days, _) in jobs.items()])
    model.minimize(makespan)
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1
    status = solver.solve(model)
    if status != cp_model.OPTIMAL:
        return {}
    return {name: solver.value(start[name]) for name in jobs}


if __name__ == "__main__":
    print(paving_plan({"elm": (3, 2), "oak": (2, 1), "ash": (4, 1)}, 3, 20))
