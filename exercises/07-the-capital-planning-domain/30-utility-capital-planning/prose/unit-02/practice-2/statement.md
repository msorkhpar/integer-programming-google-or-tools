A gas utility (a fictional one) plans its fleets (mains, valves, regulators) with the same
multi-period model as GridCap: a binary $`x_{i,t}`$ for every project $`i`$ and every start year
$`t`$ from its earliest to its latest. When a test of the model fails, the first question is
"which rows does this project's variables appear in?". Write the function that answers it.

The model's rows, with the names the code gives them:

- `must_<id>` if the project is a must-do, otherwise `once_<id>`: the sum of its start variables.
- `alt_<group>` for a project in an alternative group.
- `after_<child>_<t>` for each child project and each of the child's start years $`t`$:
  $`\text{by}(\text{child}, t) \le \text{by}(\text{parent}, t - \text{lag})`$, where
  $`\text{by}(i, t)`$ is the sum of project $`i`$'s start variables for years up to $`t`$. A
  variable appears in a row only if the row has a term for it.
- `budget_<y>` for each plan year $`y`$, summing the spend of every project at work in $`y`$; a
  project started in $`t`$ with a duration of $`d`$ years is at work in years $`t`$ to
  $`t + d - 1`$.
- `crew_<program>_<y>`, the same as the budget row but one per program.

Write `rows_for(pid, projects, years)` in `rows.py`: the set of row names in which at least one
of project `pid`'s start variables appears. Only years in `years` have budget and crew rows.

A parent's variable is in a child's `after_<child>_<t>` row only when the row's right-hand side can
reach it: $`\text{by}(\text{parent}, t - \text{lag})`$ sums the parent's starts up to
$`t - \text{lag}`$, so the parent appears exactly when $`t - \text{lag}`$ is at least the parent's
earliest start. Worked example: a parent P that may start only in 2028, and its child C (start 2028
to 2030, lag 1).

- `after_C_2028`: the right side is $`\text{by}(P, 2027)`$, which sums no variable of P (P cannot
  start by 2027), so P is not in this row.
- `after_C_2029`: the right side is $`\text{by}(P, 2028) = x_{P,2028}`$, so P is in it.
- `after_C_2030`: the right side is $`\text{by}(P, 2029) = x_{P,2028}`$, so P is in it.

So P's rows are `once_P`, `after_C_2029`, `after_C_2030` and its budget and crew rows for 2028; C's
own variables are in all three of C's after rows. The tests use small hand-made fleets. About
fifteen lines.
