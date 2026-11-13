Your capstone's planning model now meets the practice portfolio: the same fictional utility, the
same snapshot format, and every rule its data carries. Build the whole model in MathOpt and solve it
with HiGHS to a zero gap. The tests do not read your rows. They fix whole plans by their variable
bounds and ask the model to accept or refuse each one, so any correct formulation passes, and they
compare the best plan's NPV with the reference.

**Write the formulation first**, on paper or in a comment, in the order lesson 13.1.2 uses: the sets
(projects $`J`$, years $`Y`$, start years $`T_j`$, regions, programs, alternative groups, children
with a parent); the parameters with their units (`cost` and `npv` in $k, budgets, region budgets,
crew-months, floors, lags); the variables with their domains; the objective with its sense; and
every row with its quantifier and its label.

The starter gives you the scaffolding: `variables` creates $`x_{j,t} \in \{0, 1\}`$ for each start
year of each window (so a start outside a window has no variable), `solve`, `best` (the optimal value
and plan) and `allows` (a plan fixed by bounds, then solved). You write two functions in
`portfolio_model.py`:

| method | contract | modeling idea | lesson |
| --- | --- | --- | --- |
| `add_rules(model, x, snap)` | `once_j`/`must_j` | $`s_j = \sum_t x_{j,t}`$ at most 1, or exactly 1 for a must-do | 6.4.1, 6.5.1 |
| | `alt_g` | at most one member of a group funded | 6.5.3 |
| | `after_j_t` | started by year $`t`$ only if the parent started by $`t - L_j`$: the cumulative form, one row per $`t \in T_j`$ | 6.4.3, 6.5.2, 6.5.4 |
| | `budget_y`, `region_r_y` | spend in year $`y`$ is $`\sum_j \sum_{t \le y} c_{j,y-t}\, x_{j,t}`$, at most the limit | 6.4.2, 6.5.5 |
| | `crews_g_y` | crew-months of program $`g`$'s projects at work in year $`y`$, at most the limit | 6.4.2 |
| | `floor_r` | the whole cost of region $`r`$'s funded projects, at least the floor | 6.5.5 |
| `set_objective(model, x, snap)` | maximize $`\sum_{j,t} \text{npv}_{j,t}\, x_{j,t}`$ | each start valued at its own year | 7.2.4 |

`npv` is keyed by start year as an `int` (`snap["projects"]["J1"]["npv"][2027]`), with one entry
per start year of the window. Milestone 1 refused any window that leaves no room for the whole cost
profile, so no start spends past the horizon (if one did, that year has no `budget_y` row, and its
spend would count nowhere). A region missing from `region_budget`, a program
missing from `crews` and a region missing from `floor` get no row: that limit does not exist.
Manual overrides (lesson 6.5.6) are not part of this snapshot. A sum over an empty set is the number
0, and MathOpt refuses a row built from it: start each sum with `mathopt.LinearExpression()`. About
forty-five lines.
