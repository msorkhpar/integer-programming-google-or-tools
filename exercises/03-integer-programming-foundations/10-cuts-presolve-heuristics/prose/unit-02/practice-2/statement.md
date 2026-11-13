A vegetation-management model maximizes $`\sum_j c_j x_j`$ over $`x_j \in \{0, 1\}`$ under rows
$`\sum_j a_{r,j}\, x_j \le b_r`$. Some $`c_j`$ are negative: optional overtime shifts cost money and
are worth taking only when they let other work in. Write the dual-fixing reduction.

Write `dual_fixings(objective, rows)` in `dual.py`. `objective` maps each variable to $`c_j`$;
`rows` maps each row name to a pair `(coefs, rhs)`, where `coefs` maps the row's variables to their
$`a_{r,j}`$ (a variable in no row has no entry anywhere). Return a dict of the variables to fix:

```math
x_j = 1 \;\text{ if } c_j \ge 0 \text{ and } a_{r,j} \le 0 \;\; \forall r, \qquad
x_j = 0 \;\text{ if } c_j < 0 \text{ and } a_{r,j} \ge 0 \;\; \forall r
```

where $`r`$ runs over every row that contains $`x_j`$. This is the lesson's rule, $`c_j \ge 0`$ as in
its presolve code: a variable worth exactly 0 whose entries are all $`\le 0`$ is fixed at 1 (funding
it costs nothing and loosens its rows, so some optimal plan includes it), and a variable worth 0 with
a positive entry is left free. The reference solution tests `c >= 0` for the first case and `c < 0`
for the second.
Apply the rule once, to the model as given; don't substitute and repeat.
