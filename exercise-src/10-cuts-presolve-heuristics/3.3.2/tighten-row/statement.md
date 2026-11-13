A crew-allocation model has knapsack rows $`\sum_j a_j x_j \le b`$ with $`a_j > 0`$ and every
$`x_j \in \{0, 1\}`$ free. Before the search, presolve should tighten them, so the LP relaxation
gives a better bound with the same 0-1 plans.

Write `tighten(coefs, rhs)` in `tighten.py`. Go through the variables in sorted order of their
names. For each variable $`k`$, with the row as it is at that moment, compute

```math
\overline{L} = \sum_j a_j, \qquad d = b - (\overline{L} - a_k)
```

and if $`d > 10^{-9}`$, replace $`a_k`$ by $`a_k - d`$ and $`b`$ by $`b - d`$. Return the pair
`(new_coefs, new_rhs)`: a new dict, with the dict you were given left as it was. Each later variable
sees the row after the earlier changes.
