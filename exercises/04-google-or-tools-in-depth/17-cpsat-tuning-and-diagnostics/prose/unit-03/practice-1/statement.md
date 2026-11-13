The same planning service stores a record of each solve, so that an auditor's rerun can be compared
with the original. A record must hold only what a repeatable run repeats, and it must be the same
for two builds of the same model.

Write `record(solver, status, pick)` in `audit.py`, where `pick` maps each feeder's name to its
Boolean variable. Return a tuple of three items:

1. the status name (`"OPTIMAL"`, `"FEASIBLE"`, ...);
2. the objective value as a whole number, an `int`: `round(solver.objective_value)`, as the
   reference does. `solver.objective_value` is a float that can land just below the whole number
   (lesson 4.5.3), and `int(...)` would then cut it down by one;
3. the names of the feeders the solution picks, as a tuple in alphabetical order.

Leave out anything that measures the clock. About three lines.
