A transit agency's maintenance LP came back `INFEASIBLE`. Before anyone hunts for the culprit
row, the planners want one number: how far apart are the rows? Zero would mean the report was
wrong; anything above zero is the least total amount by which the rows must be relaxed.

Write `total_violation(rows)` in `violation.py`. Each row is `(a, sense, b)`: a list of
coefficients, `"<="` or `">="`, and a right-hand side. The decision variables are
$`x_j \ge 0`$, one per coefficient. Build and solve, with GLOP, the phase-1 LP that gives every row
$`r`$ an elastic variable $`v_r`$:

```math
\begin{aligned}
\min \;& \sum_{r} v_r \\
\text{s.t. }& a_r \cdot x - v_r \le b_r && \forall r \text{ with sense } \le && \text{(stretched}_r) \\
& a_r \cdot x + v_r \ge b_r && \forall r \text{ with sense } \ge && \text{(stretched}_r) \\
& x_j \ge 0 \ \ \forall j, \qquad v_r \ge 0 \ \ \forall r
\end{aligned}
```

and return its optimal value, a float. This LP always has an optimum (any $`x`$ fits once the
$`v_r`$ are large enough, and the sum cannot go below 0), so there is no other status to handle.
