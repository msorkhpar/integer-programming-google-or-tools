A port's berth-allocation MILP feeds a dashboard that shows one badge per run. The team wants the
badge to answer two questions before anyone looks at the numbers: is there a plan to use, and could
more search still change the answer?

Write `verdict(termination)` in `verdict.py`. `termination` is a `mathopt.Termination`, the
`termination` field of a `SolveResult`. Return a dict with three keys:

- `"has_plan"`: `True` when the reason is `OPTIMAL` or `FEASIBLE`, and `False` for any other reason.
- `"settled"`: `True` when the reason is `OPTIMAL` (the bounds are within the gap tolerances, even
  if they are not equal) or `INFEASIBLE` (no plan exists), and `False` for any other reason.
- `"limit"`: the name of `termination.limit` (`"TIME"`, `"NODE"`, `"SOLUTION"`, `"UNDETERMINED"`,
  ...) when the reason is `FEASIBLE` or `NO_SOLUTION_FOUND`, and `None` for any other reason.

A `Limit` member's name is its `.name` attribute: `mathopt.Limit.NODE.name` is `"NODE"`. Read the
reason from `termination.reason` and compare it with the members of `mathopt.TerminationReason`.
