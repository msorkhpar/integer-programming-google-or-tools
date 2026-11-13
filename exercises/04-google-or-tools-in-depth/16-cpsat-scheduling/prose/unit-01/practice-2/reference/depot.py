from __future__ import annotations

from ortools.sat.python import cp_model


def plan_depot(buses: dict[str, list[tuple[str, int]]]) -> dict[tuple[str, int], int]:
    """Start hour of each step (bus, k), so the last bus leaves as early as possible."""
    horizon = sum(hours for steps in buses.values() for _, hours in steps)
    model = cp_model.CpModel()
    start, on_bay, last_ends = {}, {}, []
    for bus, steps in buses.items():
        for k, (bay, hours) in enumerate(steps):
            start[bus, k] = model.new_int_var(0, horizon, f"start_{bus}_{k}")
            interval = model.new_fixed_size_interval_var(start[bus, k], hours, f"{bus}_{k}")
            on_bay.setdefault(bay, []).append(interval)
        for k in range(len(steps) - 1):
            model.add(start[bus, k + 1] >= start[bus, k] + steps[k][1])
        last_ends.append(start[bus, len(steps) - 1] + steps[-1][1])
    for intervals in on_bay.values():
        model.add_no_overlap(intervals)

    makespan = model.new_int_var(0, horizon, "makespan")
    model.add_max_equality(makespan, last_ends)
    model.minimize(makespan)
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1
    solver.solve(model)
    return {key: solver.value(var) for key, var in start.items()}


if __name__ == "__main__":
    print(plan_depot({"bus1": [("wash", 1), ("service", 3)], "bus2": [("service", 2), ("wash", 1)]}))
