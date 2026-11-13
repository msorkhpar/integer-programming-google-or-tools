A freight company's depot-siting MILP has been running for an hour. While it runs, managers keep
asking the same kind of question: "is there a plan worth at least 5,200?", or, on the cost model,
"can we do it for 3,000 or less?". The solver's two numbers answer each question in one of three
ways, without waiting for the end.

Write `judge_claim(value, incumbent, bound, maximize)` in `claims.py`. `incumbent` is the value of
the best plan found so far, or `None` when no plan has been found yet. `bound` is the best bound.
`maximize` is `True` for a maximization and `False` for a minimization. The claim is "a plan at least
as good as `value` exists" (at least `value` when maximizing, at most `value` when minimizing).
Return:

- `"found"` when the incumbent already is such a plan: for a maximization `value <= incumbent`, for a
  minimization `value >= incumbent`.
- `"impossible"` when the bound rules it out: for a maximization `value > bound`, for a minimization
  `value < bound`.
- `"possible"` otherwise: the claim lies inside the bracket, and only more search can settle it.

With `incumbent` set to `None`, no claim is `"found"`, and a claim the bound does not rule out is
`"possible"`: not having found a plan yet is not a proof that none exists.
