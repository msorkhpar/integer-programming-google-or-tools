A hospital schedules its operating theatres with a MILP every night, and the job is now run twice
to check it. Each run gives a dict: `status` (a string such as `"OPTIMAL"` or `"FEASIBLE"`),
`objective` (a float) and `plan`, a dict from each surgery's id to its theatre, for example
`{"S1": "T2", "S2": "T1"}`.

Write `verdict(first, second, tol)` that returns one word for the pair:

- `"same"`: the two runs stopped for the same reason, their objectives are within `tol` of each
  other, and they made the same assignments;
- `"tie"`: the same status and objectives within `tol`, but different assignments: an equally good
  other plan;
- `"different"`: anything else.

About five lines.
