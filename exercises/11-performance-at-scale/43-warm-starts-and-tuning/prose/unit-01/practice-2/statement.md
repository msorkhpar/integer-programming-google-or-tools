A water utility renews pipe in one-year jobs. Each job $`j`$ has a cost $`c_j`$ ($k, all spent in
the year it is done), a value $`v_j`$ ($k), the years $`Y_j`$ it may be done in (earliest first),
and a must-do flag. Each year $`y`$ has a budget $`B_y`$. The planners' model has a binary
$`x_{j,y}`$ for each job and each $`y \in Y_j`$, at most one year per job (exactly one for a
must-do), and one budget row per year. Solves are stopped early on busy nights, so they want a
plan in hand from the first moment: a greedy one, handed to the solver as a start.

Before you code, write the greedy rule as an order on the jobs and a placement rule: which jobs
come first, how the others are ranked (ties by name), and which year a job takes given the money
left in each year, $`B_y - \sum_{j' \text{ placed in } y} c_{j'}`$. A job that fits no year is left
out. The must-do jobs come first and are ranked among themselves by the same rule as the others, so
when two must-do jobs compete for one year, the one with more value per $k gets it.

Write two functions in `renewal.py`:

- `greedy_plan(jobs, budget)` returns `{job name: year}` for the jobs the rule places.
- `as_hint(x, plan)` turns a plan into a `mathopt.SolutionHint` for the variables `x[(name, year)]`.
  Give the solver a complete start, as lesson 11.2.1 does.

One test builds the model and asks HiGHS, through MathOpt, whether it accepts your start, by
reading its log. About fifteen lines.
