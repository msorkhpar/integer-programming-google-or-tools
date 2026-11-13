A dispatch team (not GridCap) runs CP-SAT models of many shapes from one service, and the service
has to tell its callers what came back. Last week it returned "plan: []" for a model the solver had
refused, and the caller read that as "load nothing".

Write `report(model, x, solver=None)` in `report.py`. `x` maps names to the model's Boolean
variables; `solver` is a `CpSolver` the caller may have configured (make a new one when it is
`None`). Solve the model once and return a dict with five keys:

| Key | Value |
| --- | --- |
| `"status"` | the status's name, such as `"OPTIMAL"` |
| `"plan"` | the sorted names whose Boolean is true, when the status carries a solution; else `None` |
| `"objective"` | the objective value rounded to an `int`, when there is a solution *and* the model has an objective; else `None` |
| `"proven"` | `True` only when the solution was proved best |
| `"reason"` | for an invalid model, the solver's explanation of what is wrong; else `""` |

Use the lesson's table of the five statuses to decide which ones carry a solution.
`model.has_objective()` says whether an objective was set. The tests build small models of each
kind, including a search the caller stops at its first plan. About twelve lines.
