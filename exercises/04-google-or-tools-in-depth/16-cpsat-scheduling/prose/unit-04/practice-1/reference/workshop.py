from __future__ import annotations

from ortools.sat.python import cp_model


def least_penalty(jobs: dict[str, tuple[int, int, int, int]], mechanics: int,
                  horizon: int) -> tuple[int, dict[str, int]]:
    """(least total penalty, start day of each job) under a pool of mechanics."""
    model = cp_model.CpModel()
    start, late, intervals, demands = {}, {}, [], []
    for name, (days, need, due, _) in jobs.items():
        start[name] = model.new_int_var(0, horizon - days, f"start_{name}")
        intervals.append(model.new_fixed_size_interval_var(start[name], days, f"repair_{name}"))
        demands.append(need)
        late[name] = model.new_int_var(0, horizon, f"late_{name}")
        model.add_max_equality(late[name], [0, start[name] + days - due])
    model.add_cumulative(intervals, demands, mechanics)
    model.minimize(sum(penalty * late[name] for name, (_, _, _, penalty) in jobs.items()))
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1
    solver.solve(model)
    return round(solver.objective_value), {name: solver.value(start[name]) for name in jobs}


if __name__ == "__main__":
    print(least_penalty({"lathe": (3, 1, 3, 5), "press": (2, 2, 4, 9), "pump": (2, 1, 2, 1)}, 2, 20))
