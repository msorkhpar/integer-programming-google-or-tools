A hospital's staffing service solves a nurse-rostering model every evening and hands the answer to
three callers: a dashboard, a nightly report and an alerting job. Each caller only needs to know what
to do with the result. Write `verdict(result)` in `verdict.py`, which reads a `mathopt.SolveResult`
and returns a `Verdict` with four fields:

| `termination.reason` | `action` | `value` | `gap` | `limit` |
| --- | --- | --- | --- | --- |
| `OPTIMAL` | `"use"` | the objective value | `0.0` | `None` |
| `FEASIBLE` | `"use-with-gap"` | the objective value | $`\lvert \text{dual bound} - \text{primal bound} \rvert`$ | the limit's name, such as `"SOLUTION"` |
| `NO_SOLUTION_FOUND` | `"retry"` | `None` | `None` | the limit's name |
| `INFEASIBLE` | `"conflict"` | `None` | `None` | `None` |
| `UNBOUNDED`, `INFEASIBLE_OR_UNBOUNDED` | `"model-error"` | `None` | `None` | `None` |
| `IMPRECISE`, `NUMERICAL_ERROR`, `OTHER_ERROR` | `"solver-error"` | `None` | `None` | `None` |

An `UNBOUNDED` result may carry a feasible point; it is still a model error, and its value is `None`.
A limit's name is `result.termination.limit.name` (a `Limit` such as `Limit.SOLUTION` has the name
`"SOLUTION"`). The tests build their results by solving small models of their own, and a few by
constructing a `SolveResult` directly.
