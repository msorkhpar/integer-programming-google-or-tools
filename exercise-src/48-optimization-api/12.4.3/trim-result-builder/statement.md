A trim job has finished. The worker knows how it ended (`status`, `message`), the plan's value
(outage-minutes avoided per year, or `None` when there is no plan), the solver's best bound, and the
circuits chosen. The scheduling tool wants a `TrimResult` (the schema is in the file) it can draw
as-is.

Write `build_result(status, message, value, bound, chosen, work, capacity)` in `trim_builder.py`:

- `circuits`: the chosen circuit ids, sorted.
- `hours_by_month`: one row for every month in `capacity`, in increasing month order, with the crew
  hours the chosen circuits need that month (`work[circuit] = (month, crew_hours)`), 0 for a month
  with no work, and that month's capacity. A result with no plan has no rows.
- `bound`: the solver's bound, except that an infinite bound (what a solve with no plan reports)
  becomes `None`. JSON has no infinity, and the result must read back from its own JSON.
- `gap`: `(bound - value) / |value|`, with 1 as the smallest divisor so a plan worth 0 still has a
  gap; `None` when there is no value or no finite bound. The job maximizes, so a bound below the
  value means the plan is proven: clamp that gap to 0, never report it negative (the schema's
  `ge=0` refuses a negative gap).

The tests call `build_result` with small hand-made jobs. About fifteen lines.
