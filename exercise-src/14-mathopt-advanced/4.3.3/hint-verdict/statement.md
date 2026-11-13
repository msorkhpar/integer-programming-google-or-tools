A planning service passes a solution hint on every solve and keeps each solve's log. Its dashboard
should show, per solve, what the solver did with the hint. Write `hint_verdict(solver, log)`, where
`solver` is `"HIGHS"`, `"GSCIP"` or `"CP_SAT"` and `log` is the list of log lines. It returns one of
`"accepted"`, `"partial"`, `"repairing"`, `"rejected"` or `"unknown"`, from these lines (lesson
4.3.3 shows them all):

| Solver | A line containing | Verdict |
| --- | --- | --- |
| HiGHS | `Attempting to find feasible solution by solving MIP for user-supplied values` | `partial` |
| HiGHS | `cannot yield feasible solution` | `rejected` |
| HiGHS | `MIP start solution is feasible` | `accepted` |
| SCIP | `feasible solution given by solution candidate storage` | `accepted` |
| CP-SAT | `The solution hint is complete and is feasible` | `accepted` |
| CP-SAT | `The solution hint is incomplete` | `partial` |
| CP-SAT | `The solution hint is complete, but it is infeasible` | `repairing` |

When a log has lines for more than one verdict, the first row of the table that matches wins:
HiGHS logs a completed partial hint with both its "Attempting" line and a "MIP start solution is
feasible" line, and that hint was partial. A log with none of its solver's lines is `"unknown"`:
silence is not evidence either way. About twelve lines.
