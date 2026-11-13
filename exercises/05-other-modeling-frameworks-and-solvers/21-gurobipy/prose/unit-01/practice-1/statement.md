A crew-rostering service solves its MIP with gurobipy and must decide, after every solve, what to do
with the result. All it has are two model attributes: `Status`, the optimization status code, and
`SolCount`, the number of feasible plans Gurobi kept. Write `outcome(status, sol_count)`, which
returns one of these strings:

| `status` (gurobipy constant) | `sol_count` | Return |
| --- | --- | --- |
| `GRB.OPTIMAL` | any | `"use"` |
| `GRB.ITERATION_LIMIT`, `GRB.NODE_LIMIT`, `GRB.TIME_LIMIT`, `GRB.SOLUTION_LIMIT`, `GRB.WORK_LIMIT`, `GRB.MEM_LIMIT`, `GRB.INTERRUPTED` | more than 0 | `"use, report gap"` |
| the same seven | 0 | `"no plan: limit"` |
| `GRB.INFEASIBLE` | any | `"no plan: infeasible"` |
| `GRB.INF_OR_UNBD` | any | `"no plan: re-solve with DualReductions=0"` |
| `GRB.UNBOUNDED` | any | `"no plan: unbounded"` |
| anything else | any | `"no plan: solver failure"` |

Compare with the constants (`from gurobipy import GRB`), never with bare numbers. Importing gurobipy
and reading its constants needs no license, so this practice runs without one. About fifteen lines.
