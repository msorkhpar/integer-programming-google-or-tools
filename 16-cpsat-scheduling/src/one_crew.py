"""Lesson 4.5.1: one crew, five circuit jobs, and NoOverlap; then weeks the crew cannot work.

Patterned on the OR-Tools sample no_overlap_sample_sat.py (tasks around fixed weekend intervals),
https://github.com/google/or-tools/blob/stable/ortools/sat/samples/no_overlap_sample_sat.py.
GridCap is fictional.
"""

from ortools.sat.python import cp_model

from cpsat_run import solve
from season import HORIZON, by_id

job = by_id()
WORK = ["P003", "P010", "P011", "P014", "P015"]           # Valley and Coast circuits, one crew each
BLOCKED = {"training": (8, 1), "storm standby": (12, 2)}    # (first week, weeks)


def schedule(blocked: dict[str, tuple[int, int]]) -> None:
    model = cp_model.CpModel()
    start, end, task = {}, {}, {}
    for j in WORK:
        start[j] = model.new_int_var(0, HORIZON, f"start_{j}")
        end[j] = model.new_int_var(0, HORIZON, f"end_{j}")
        task[j] = model.new_interval_var(start[j], job[j].weeks, end[j], f"work_{j}")
    fixed = [model.new_fixed_size_interval_var(first, weeks, name) for name, (first, weeks) in blocked.items()]
    model.add_no_overlap(list(task.values()) + fixed)

    makespan = model.new_int_var(0, HORIZON, "makespan")
    model.add_max_equality(makespan, [end[j] for j in WORK])
    model.minimize(makespan)

    solver, status = solve(model)
    print(f"{status}: makespan {solver.value(makespan)} weeks, {sum(job[j].weeks for j in WORK)} weeks of work")
    rows = [(solver.value(start[j]), solver.value(end[j]), j) for j in WORK]
    rows += [(first, first + weeks, name) for name, (first, weeks) in blocked.items()]
    for s, e, name in sorted(rows):
        print(f"  weeks {s:>2}-{e - 1:>2}  {name}")


if __name__ == "__main__":
    print("no blocked weeks")
    schedule({})
    print("training in week 8, storm standby in weeks 12-13")
    schedule(BLOCKED)
