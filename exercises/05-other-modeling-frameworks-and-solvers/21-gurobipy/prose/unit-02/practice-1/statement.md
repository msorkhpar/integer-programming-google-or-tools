A furniture workshop's LP has been solved, and the team has its row prices (`Pi`) but wants to
check the reduced costs and whether the basis is optimal, by hand. For an LP with objective
coefficients $`c_j`$, row coefficients $`a_{ij}`$ and row prices $`\pi_i`$, the reduced cost of
column $`j`$ is

```math
\text{RC}_j = c_j - \sum_i a_{ij}\, \pi_i
```

Write two functions.

**`reduced_costs(c, A, pi)`**: `c` is a list of objective coefficients, `A` a list of rows (each a
list with one coefficient per column), `pi` a list of row prices. Return the list of reduced costs,
one per column.

**`wrong_signs(rc, where, maximize, tol=1e-9)`**: `where[j]` says where variable $`j`$ sits: `"basic"`,
`"lower"` (at its lower bound) or `"upper"` (at its upper bound). At an optimal basis:

| `where[j]` | maximize | minimize |
| --- | --- | --- |
| `"basic"` | $`\lvert\text{RC}_j\rvert \le`$ tol | $`\lvert\text{RC}_j\rvert \le`$ tol |
| `"lower"` | $`\text{RC}_j \le`$ tol | $`\text{RC}_j \ge -`$tol |
| `"upper"` | $`\text{RC}_j \ge -`$tol | $`\text{RC}_j \le`$ tol |

Return the sorted indices $`j`$ that break their rule (an empty list means the basis passes). No
Gurobi license is needed. About fifteen lines.
