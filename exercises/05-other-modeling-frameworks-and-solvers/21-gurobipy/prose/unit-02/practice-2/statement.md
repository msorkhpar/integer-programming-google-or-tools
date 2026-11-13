A regional transit agency solves an LP in gurobipy and keeps, for one row, its attributes after the
solve: the optimal objective `ObjVal`, the row's price `Pi`, its right-hand side `RHS`, and its range
`SARHSLow` to `SARHSUp`. Planners ask "what if this row's right-hand side were `new_rhs`?" many times
a day, and a re-solve each time is too slow.

Write `forecast(objval, pi, rhs, low, up, new_rhs)`. Inside the range, including both ends, the
current basis stays optimal and the objective moves linearly:

```math
\text{forecast} = \text{ObjVal} + \pi\,(\text{new\_rhs} - \text{RHS}) \qquad \text{if } \text{low} \le \text{new\_rhs} \le \text{up}
```

Outside the range the price no longer holds, and the function returns `None` (a re-solve is
needed). Use `Pi` with its sign as given: in a minimization a $`\le`$ row's price is negative, and
more capacity then lowers the cost. `low` and `up` may be infinite (`float("inf")`). No Gurobi
license is needed. About five lines.
