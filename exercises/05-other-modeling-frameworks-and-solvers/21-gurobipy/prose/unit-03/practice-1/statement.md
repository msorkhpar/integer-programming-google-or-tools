A hospital's nurse-rostering model came back `INFEASIBLE`, and `computeIIS()` has run. The team
has copied what it set into plain data (so the report can be written and tested anywhere, even
without a license):

- `status`: the model's `Status` code;
- `rows`: one dict per linear row, `{"name": ConstrName, "sense": Sense, "rhs": RHS, "iis": IISConstr}`,
  where `Sense` is `"<"`, `">"` or `"="` as gurobipy reports it;
- `bounds`: one dict per variable, `{"name": VarName, "lb": LB, "ub": UB, "iis_lb": IISLB, "iis_ub": IISUB}`.

Write `iis_report(status, rows, bounds)`, which returns sorted lines for a planner:

| In the IIS | Line |
| --- | --- |
| a row with `iis` 1 | `"<name> <= <rhs>"`, `"<name> >= <rhs>"` or `"<name> == <rhs>"`, by its sense |
| a variable with `iis_lb` 1 | `"<name> >= <lb>"` |
| a variable with `iis_ub` 1 | `"<name> <= <ub>"` |

Numbers are written with `:g` (`40.0` prints as `40`). Only what the IIS marks is listed. If `status`
is not `GRB.INFEASIBLE` (`from gurobipy import GRB`), there is no IIS to read, and the function
returns an empty list. About twelve lines.
