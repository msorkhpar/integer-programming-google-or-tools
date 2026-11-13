The planning tool rejects plans, and planners keep asking *why*. A rejection that only says
"infeasible" sends them to the spreadsheet; one that names the broken rule lets them fix the plan
in a minute.

Write `evaluate_plan(projects, budget, plan)` in `plans.py`. It returns a pair: the plan's total
value, and a list of problems, one string for each rule the plan breaks:

| problem | when |
| --- | --- |
| `"budget"` | the plan's total cost is over `budget` |
| `"must-do:<id>"` | a must-do project is not in the plan (one string per missing project) |
| `"parent:<id>"` | project `<id>` is in the plan and its parent is not |
| `"alternatives:<group>"` | the plan holds more than one project of alternative group `<group>` |

An allowed plan returns its value and an empty list. The order of the problems does not matter.
`projects` is a list of `Project` records (defined at the top of the file) and `plan` is a set of
project ids.

About ten lines in total.
