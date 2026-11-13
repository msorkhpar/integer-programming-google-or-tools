This is the mock's whiteboard, coded for CP-SAT. A substation inspection crew does one job at a
time. `crew.py` already has one integer start week per job, from its release week to the last
start that ends by the horizon, and the objective (the sum of the jobs' end weeks). A job of
`duration` weeks started in week $`s`$ works weeks $`s`$ to $`s + \text{duration} - 1`$ and ends at
$`s + \text{duration}`$. Three rules are missing:

- **One crew.** No two jobs work in the same week.
- **Blocked periods.** Each pair `(first, last)` in `blocked` is a block of weeks, both ends
  included, in which the crew does no work.
- **Deadlines.** Each job's end is at most its `deadline`.

Write `add_rules(model, start, jobs, blocked)`. Write the formulation first (variables with their
domains, then each constraint with a label), and use CP-SAT's native constraints for the crew rule.

The tests fix every start week and ask CP-SAT, with one worker, whether the model accepts the
schedule, so any correct formulation passes. About eight lines.
