A team is porting a pump-scheduling model from pywraplp to MathOpt. Their agreement test needs to
ask the *old* model whether the *new* model's plan is allowed, without solving anything.

Write `allowed(solver, values, tol=1e-6)` in `check.py`. `solver` is a pywraplp solver holding a
model (it need not have been solved), and `values` maps every variable's name to a value. Return
`True` when the plan keeps every rule of the model, within `tol`:

```math
\begin{aligned}
& \ell_j - \text{tol} \le v_j \le u_j + \text{tol} && \text{for every variable } j \text{ (its bounds)} \\
& |v_j - \operatorname{round}(v_j)| \le \text{tol} && \text{for every integer variable } j \\
& \text{lb}_r - \text{tol} \le \sum_j a_{r,j}\, v_j \le \text{ub}_r + \text{tol} && \text{for every row } r
\end{aligned}
```

Read the model back with the calls lesson 4.7.1 listed: `solver.variables()` and
`solver.constraints()`, and on them `name()`, `lb()`, `ub()`, `Integer()` and
`GetCoefficient(var)`. A row with no lower bound has `lb()` equal to `-inf`, so the same comparison
works for every row. About ten lines.
