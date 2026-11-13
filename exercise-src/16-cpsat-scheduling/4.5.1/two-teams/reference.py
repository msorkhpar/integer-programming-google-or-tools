from __future__ import annotations

from ortools.sat.python import cp_model


def split_work(jobs: dict[str, int], teams: list[str], away: dict[str, list[tuple[int, int]]],
               horizon: int) -> dict[str, tuple[str, int]]:
    """(team, start day) for each job, so the last job ends as early as possible."""
    model = cp_model.CpModel()
    start, does = {}, {}
    on_team = {t: [] for t in teams}
    for j, days in jobs.items():
        start[j] = model.new_int_var(0, horizon - days, f"start_{j}")
        for t in teams:
            does[j, t] = model.new_bool_var(f"{t}_does_{j}")
            on_team[t].append(model.new_optional_fixed_size_interval_var(start[j], days, does[j, t], f"{j}_by_{t}"))
        model.add_exactly_one(does[j, t] for t in teams)
    for t in teams:
        for first, last in away.get(t, []):
            on_team[t].append(model.new_fixed_size_interval_var(first, last - first + 1, f"{t}_away_{first}"))
        model.add_no_overlap(on_team[t])

    makespan = model.new_int_var(0, horizon, "makespan")
    model.add_max_equality(makespan, [start[j] + days for j, days in jobs.items()])
    model.minimize(makespan)
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1
    solver.solve(model)
    return {j: (next(t for t in teams if solver.boolean_value(does[j, t])), solver.value(start[j])) for j in jobs}


if __name__ == "__main__":
    print(split_work({"main_st": 3, "mill_rd": 2, "dam": 4}, ["red", "blue"], {"blue": [(0, 1)]}, 20))
