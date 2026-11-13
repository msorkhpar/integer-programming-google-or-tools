A school-bus planner ran `feasRelax` on an infeasible routing model, solved it, and saved every
variable's name and value as a dict `values` (`VarName` to `X`). The relaxation's artificial
variables say what had to give. Gurobi names them by prefix:

| Prefix | Added to | Meaning of a value $`v > 0`$ | Line |
| --- | --- | --- | --- |
| `ArtP_<row>` | the row, with $`+1`$ | the row's left side fell short by $`v`$ | `"<row>: short by <v>"` |
| `ArtN_<row>` | the row, with $`-1`$ | the row's left side ran over by $`v`$ | `"<row>: over by <v>"` |
| `ArtL_<var>` | the variable's lower bound | the variable went below its lower bound by $`v`$ | `"<var>: below its lower bound by <v>"` |
| `ArtU_<var>` | the variable's upper bound | the variable went above its upper bound by $`v`$ | `"<var>: above its upper bound by <v>"` |

Write `relaxation_changes(values, tol=1e-6)`, which returns the sorted lines for every artificial
variable with a value above `tol`. Numbers are written with `:g`. Everything else in `values` is
not a change: the model's own variables, and the binaries a counting relaxation adds, whose names
start `ArtPB_`, `ArtNB_`, `ArtLB_` and `ArtUB_`. No Gurobi license is needed. About twelve lines.
