"""Lesson 6.2.4: OR-Tools' job shop, whose no-overlap rule is this lesson's disjunction on every machine.

Three jobs of two or three tasks on three machines; a job's tasks run in order, a machine runs one
task at a time, and the goal is the earliest finish of the last job (the makespan). CP-SAT states
the machine rule with interval variables and add_no_overlap; a MILP needs one disjunction per pair
of tasks on a machine, written here with the big-M and hull rows of outage_model.py.
"""
# Adapted from the OR-Tools example minimal_jobshop_sat.py, https://github.com/google/or-tools/blob/stable/ortools/sat/samples/minimal_jobshop_sat.py

import collections
from itertools import combinations

from ortools.math_opt.python import mathopt
from ortools.sat.python import cp_model

from crew_model import quiet_solve
from outage_model import add_big_m, add_hull

JOBS = [  # task = (machine, processing time)
    [(0, 3), (1, 2), (2, 2)],  # job 0
    [(0, 2), (2, 1), (1, 4)],  # job 1
    [(1, 4), (2, 3)],          # job 2
]
HORIZON = sum(d for job in JOBS for _, d in job)       # every task one after another: 21
TASKS = {f"j{j}t{k}": (machine, d) for j, job in enumerate(JOBS) for k, (machine, d) in enumerate(job)}


def cpsat_makespan() -> int:
    model = cp_model.CpModel()
    start, end, on_machine = {}, {}, collections.defaultdict(list)
    for name, (machine, d) in TASKS.items():
        start[name] = model.new_int_var(0, HORIZON, f"start_{name}")
        end[name] = model.new_int_var(0, HORIZON, f"end_{name}")
        on_machine[machine].append(model.new_interval_var(start[name], d, end[name], f"interval_{name}"))
    for intervals in on_machine.values():
        model.add_no_overlap(intervals)                 # the disjunctions, all at once
    for j, job in enumerate(JOBS):
        for k in range(len(job) - 1):
            model.add(start[f"j{j}t{k + 1}"] >= end[f"j{j}t{k}"])
    makespan = model.new_int_var(0, HORIZON, "makespan")
    model.add_max_equality(makespan, [end[f"j{j}t{len(job) - 1}"] for j, job in enumerate(JOBS)])
    model.minimize(makespan)
    solver = cp_model.CpSolver()
    solver.solve(model)
    return round(solver.objective_value)


def mathopt_job_shop(form: str, *, integer: bool = True) -> mathopt.Model:
    model = mathopt.Model(name=f"job shop {form}")
    d = {name: dur for name, (_, dur) in TASKS.items()}
    start = {name: model.add_variable(lb=0, ub=HORIZON - d[name], name=f"s_{name}") for name in TASKS}
    makespan = model.add_variable(lb=0, ub=HORIZON, name="makespan")
    for j, job in enumerate(JOBS):
        for k in range(len(job) - 1):
            first, then = f"j{j}t{k}", f"j{j}t{k + 1}"
            model.add_linear_constraint(start[first] + d[first] <= start[then], name=f"order_{first}")
        last = f"j{j}t{len(job) - 1}"
        model.add_linear_constraint(start[last] + d[last] <= makespan, name=f"makespan_{j}")
    for a, b in combinations(TASKS, 2):
        if TASKS[a][0] == TASKS[b][0]:                  # same machine: a before b, or b before a
            y = model.add_variable(lb=0, ub=1, is_integer=integer, name=f"first_{a}_{b}")
            (add_big_m if form == "big_m" else add_hull)(model, start, d, HORIZON, a, b, y)
    model.minimize(makespan)
    return model


if __name__ == "__main__":
    print(f"{len(TASKS)} tasks on 3 machines, horizon {HORIZON}")
    print("CP-SAT, add_no_overlap: makespan", cpsat_makespan())
    for form in ("big_m", "hull"):
        lp = quiet_solve(mathopt_job_shop(form, integer=False), mathopt.SolverType.GLOP)
        milp = quiet_solve(mathopt_job_shop(form), mathopt.SolverType.HIGHS)
        print(f"MathOpt, {form:6} LP bound {lp.objective_value():5.2f}  MILP makespan {milp.objective_value():.0f}")
    load = collections.Counter()
    for machine, d in TASKS.values():
        load[machine] += d
    print("work per machine:", dict(sorted(load.items())))
