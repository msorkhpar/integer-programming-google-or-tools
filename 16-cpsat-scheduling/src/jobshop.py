"""Lesson 4.5.1: the job shop. One NoOverlap per machine, one precedence row per pair of steps.

Adapted from the OR-Tools job shop example, "The Job Shop Problem",
https://developers.google.com/optimization/scheduling/job_shop (Apache-2.0). The model is the
example's; the code is rewritten so the GridCap version in jobshop_crews.py can reuse it.
"""

from __future__ import annotations

from ortools.sat.python import cp_model

from cpsat_run import solve


def jobshop(jobs: dict[str, list[tuple[str, int]]]) -> None:
    """jobs[name] is the job's steps in order, each (machine, duration). Print the best schedule."""
    horizon = sum(d for steps in jobs.values() for _, d in steps)
    model = cp_model.CpModel()
    start, end, on_machine = {}, {}, {}
    for name, steps in jobs.items():
        for k, (machine, duration) in enumerate(steps):
            start[name, k] = model.new_int_var(0, horizon, f"start_{name}_{k}")
            end[name, k] = model.new_int_var(0, horizon, f"end_{name}_{k}")
            interval = model.new_interval_var(start[name, k], duration, end[name, k], f"{name}_{k}")
            on_machine.setdefault(machine, []).append(interval)
    for intervals in on_machine.values():
        model.add_no_overlap(intervals)                               # one step at a time per machine
    for name, steps in jobs.items():
        for k in range(len(steps) - 1):
            model.add(start[name, k + 1] >= end[name, k])            # a job's steps in order

    makespan = model.new_int_var(0, horizon, "makespan")
    model.add_max_equality(makespan, [end[name, len(steps) - 1] for name, steps in jobs.items()])
    model.minimize(makespan)
    solver, status = solve(model)

    print(f"{status}: makespan {solver.value(makespan)} (horizon {horizon})")
    for machine in sorted(on_machine):
        steps = sorted((solver.value(start[name, k]), name, k, d)
                       for name, job_steps in jobs.items() for k, (m, d) in enumerate(job_steps) if m == machine)
        print(f"  {machine:<10} " + "  ".join(f"{name}#{k}[{s},{s + d}]" for s, name, k, d in steps))


if __name__ == "__main__":
    # The documentation's data: job -> [(machine, processing time), ...] in order.
    jobshop({"job0": [("machine0", 3), ("machine1", 2), ("machine2", 2)],
             "job1": [("machine0", 2), ("machine2", 1), ("machine1", 4)],
             "job2": [("machine1", 4), ("machine2", 3)]})
