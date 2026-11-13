"""Lesson 6.1.3: OR-Tools' nurse scheduling, where every rule is an exactly-one, at-most-one or count row.

Four nurses, three days, three shifts a day. Each shift gets exactly one nurse, each nurse works at
most one shift a day, and the shifts are spread so each nurse works between a minimum and a maximum.
"""
# Adapted from the OR-Tools example nurses_sat.py, https://github.com/google/or-tools/blob/stable/ortools/sat/samples/nurses_sat.py

from ortools.sat.python import cp_model

NURSES, DAYS, SHIFTS = range(4), range(3), range(3)


class Count(cp_model.CpSolverSolutionCallback):
    def __init__(self):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.solutions = 0

    def on_solution_callback(self) -> None:
        self.solutions += 1


def schedules(min_shifts: int, max_shifts: int | None) -> tuple[str, int]:
    """The solver's status and how many schedules obey the rules (all of them are enumerated)."""
    model = cp_model.CpModel()
    shifts = {(n, d, s): model.new_bool_var(f"shift_n{n}_d{d}_s{s}") for n in NURSES for d in DAYS for s in SHIFTS}
    for d in DAYS:
        for s in SHIFTS:
            model.add_exactly_one(shifts[n, d, s] for n in NURSES)      # one nurse per shift
    for n in NURSES:
        for d in DAYS:
            model.add_at_most_one(shifts[n, d, s] for s in SHIFTS)      # one shift per nurse and day
    for n in NURSES:
        worked = sum(shifts[n, d, s] for d in DAYS for s in SHIFTS)
        model.add(worked >= min_shifts)                                 # at least k
        if max_shifts is not None:
            model.add(worked <= max_shifts)                             # at most k
    solver = cp_model.CpSolver()
    solver.parameters.enumerate_all_solutions = True
    count = Count()
    status = solver.solve(model, count)
    return solver.status_name(status), count.solutions


total = len(DAYS) * len(SHIFTS)
low = total // len(NURSES)                         # as in the OR-Tools example: 9 // 4 = 2
high = low if total % len(NURSES) == 0 else low + 1
print(f"{total} shifts, {len(NURSES)} nurses: each works at least {low} and at most {high}")
for name, (k_min, k_max) in {"min and max": (low, high), "min only": (low, None),
                             "no spread rule": (0, None), "min 3 each": (3, None)}.items():
    status, count = schedules(k_min, k_max)
    print(f"  {name:15} {status:10} {count:6,} schedules")
print(f"precheck for min 3: {len(NURSES)} nurses x 3 = {len(NURSES) * 3} shifts wanted, {total} exist")
