from __future__ import annotations

from ortools.sat.python import cp_model


def cheapest_runs(runs: dict[str, tuple[list[int], list[int]]], deadline: int) -> tuple[int, dict[str, tuple[int, int]]]:
    """(total cost, run -> (vehicle index, start hour)) of the cheapest plan that ends by the deadline."""
    model = cp_model.CpModel()
    vehicle, start, cost, tasks = {}, {}, {}, []
    for r, (hours, costs) in runs.items():
        vehicle[r] = model.new_int_var(0, len(hours) - 1, f"vehicle_{r}")
        length = model.new_int_var(min(hours), max(hours), f"hours_{r}")
        cost[r] = model.new_int_var(min(costs), max(costs), f"cost_{r}")
        model.add_element(vehicle[r], hours, length)
        model.add_element(vehicle[r], costs, cost[r])
        start[r] = model.new_int_var(0, deadline, f"start_{r}")
        end = model.new_int_var(0, deadline, f"end_{r}")
        tasks.append(model.new_interval_var(start[r], length, end, f"run_{r}"))
    model.add_no_overlap(tasks)
    model.minimize(sum(cost.values()))
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1
    solver.solve(model)
    return round(solver.objective_value), {r: (solver.value(vehicle[r]), solver.value(start[r])) for r in runs}


if __name__ == "__main__":
    print(cheapest_runs({"north": ([4, 2], [20, 35]), "harbor": ([3, 1], [15, 30])}, 5))
