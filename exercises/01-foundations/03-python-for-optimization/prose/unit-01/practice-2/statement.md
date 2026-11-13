The budget model has one row per year and region, $`\text{spend}_{r,y} \le B_{r,y}`$ for every
$`y \in Y`$ and $`r \in R`$, so it needs exactly one valid budget $`B_{r,y} \ge 0`$ for every pair,
and nothing else. Finance sends the budgets as a CSV file with the columns `year`, `region` and
`budget`, edited by hand.

Write `budget_problems(budgets, years, regions)` in `budgets.py`. `budgets` is the file read with
`pd.read_csv` and no `dtype=`; `years` and `regions` are the plan's $`Y`$ and $`R`$. It returns one
string per problem, in any order. Line numbers count the header as line 1, so the row with index 0
is line 2.

| problem | when |
| --- | --- |
| `"line N: budget is not a number"` | the budget cell does not read as a number |
| `"line N: negative budget"` | the budget is below zero |
| `"line N: unknown region"` | the region is not in `regions` |
| `"line N: year outside the plan"` | the year is not in `years` |
| `"line N: duplicate"` | another row has the same year and region (report every such row) |
| `"missing Y R"` | no row at all has year `Y` and region `R` |

A row with a bad budget still counts as present for its year and region. An allowed table returns
an empty list.

About twelve lines.
