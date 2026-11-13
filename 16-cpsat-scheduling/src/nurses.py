"""Lesson 4.5.3: the documentation's first nurse schedule, counted rather than printed.

Adapted from the OR-Tools example "Employee Scheduling" (the nurses problem),
https://developers.google.com/optimization/scheduling/employee_scheduling (Apache-2.0):
4 nurses, 3 days, 3 shifts a day; every shift has one nurse, a nurse works at most one shift a
day, and the 9 shifts are spread so each nurse works 2 or 3.
"""

from ortools.sat.python import cp_model

NURSES, DAYS, SHIFTS = range(4), range(3), range(3)

model = cp_model.CpModel()
shifts = {(n, d, s): model.new_bool_var(f"shift_n{n}_d{d}_s{s}") for n in NURSES for d in DAYS for s in SHIFTS}
for d in DAYS:
    for s in SHIFTS:
        model.add_exactly_one(shifts[n, d, s] for n in NURSES)
for n in NURSES:
    for d in DAYS:
        model.add_at_most_one(shifts[n, d, s] for s in SHIFTS)
low = len(SHIFTS) * len(DAYS) // len(NURSES)                 # 9 // 4 = 2
high = low + (len(SHIFTS) * len(DAYS) % len(NURSES) != 0)    # 3, since 9 is not a multiple of 4
for n in NURSES:
    worked = sum(shifts[n, d, s] for d in DAYS for s in SHIFTS)
    model.add(worked >= low)
    model.add(worked <= high)


class Counter(cp_model.CpSolverSolutionCallback):
    def __init__(self):
        super().__init__()
        self.count = 0
        self.first = None

    def on_solution_callback(self):
        if self.first is None:
            self.first = {(d, s): n for (n, d, s), v in shifts.items() if self.boolean_value(v)}
        self.count += 1


solver = cp_model.CpSolver()
solver.parameters.enumerate_all_solutions = True
solver.parameters.num_workers = 1
counter = Counter()
status = solver.solve(model, counter)
print(f"{solver.status_name(status)}: {counter.count} schedules; each nurse works {low} to {high} shifts")
for d in DAYS:
    print(f"  day {d}: " + "  ".join(f"shift {s} -> nurse {counter.first[d, s]}" for s in SHIFTS))
