A water utility models its projects with gurobipy's matrix API (`addMVar`, `addMConstr`). Its
projects are given as a list of `(project_id, start_year, cost_profile)` triples: a project that
starts in year $`s`$ spends `cost_profile[k]` in year $`s + k`$. Write two functions that build the
arrays its rows need, with one column per project, in the order of the list.

**`spend_matrix(projects, years)`** returns a NumPy array $`A`$ of shape
`(len(years), len(projects))` with

```math
A_{r,j} = \text{cost\_profile}_j[k] \quad \text{where } \text{years}[r] = s_j + k
```

and 0 elsewhere. Spend that falls in a year not in `years` (after the horizon) is left out: it is
not this plan's money. Then `addMConstr(A, x, "<", B)` is the yearly budget row
$`\sum_j A_{r,j}\, x_j \le B_r`$.

**`needs_matrix(projects, parent_of)`** returns one row per entry of the dict `parent_of`
(child id to parent id), in the dict's order, with $`+1`$ in the child's column and $`-1`$ in the
parent's: then `addMConstr(N, x, "<", 0)` states $`x_c - x_{p(c)} \le 0`$, "a child is funded only
with its parent".

Both return `float` arrays. No Gurobi license is needed: the functions build arrays and never solve.
About fifteen lines.
