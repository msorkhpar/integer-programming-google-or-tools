The trim service from the earlier practices now runs as jobs, and a scheduling tool reads its
results. Each result says how the job ended, which circuits to trim, how many crew hours that takes in
each month against the crews' capacity, and how good the plan is. The tool's developers will build
screens on it, so the service must never send a result whose fields disagree with each other: an
"optimal" result with no value, or an "infeasible" one that lists circuits.

Write the rules into `TrimResult` and `MonthHours` in `trim_result.py`:

- `status` is one of `optimal`, `time_limit`, `infeasible`, `failed`, and `message` is not empty.
- `gap` is never below zero, and it is given exactly when both `value` and `bound` are.
- An `optimal` result carries a `value` (0 is a value). An `infeasible` or `failed` result carries
  no value and lists no circuits.
- A `month` is 1 to 12; `crew_hours` and `capacity` are zero or more. `hours_by_month` lists each
  month once, in increasing order, and no month's crew hours exceed its capacity.

Put the rules about one field on the field, and the rules that compare fields in one
`@model_validator(mode="after")` that raises `ValueError`. Pydantic reports either as a
`ValidationError`. The tests build results by hand, each pairing an accepted one with a refused one,
so any way of writing the rules that pydantic enforces passes.
