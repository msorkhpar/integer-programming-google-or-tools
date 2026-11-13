Budget Lock week at the practice utility (a fictional one): finance and the board send a scenario
that changes the snapshot's numbers before the run. A scenario may lock a year's `budget`, cut
`crews` (by program and year), `force_in` projects, `fix_start` a project to one year, and
`force_out` projects. Before any solve, CIPT Lite runs pre-solve checks that each read **one**
project, group or region against **one** limit, so a typed number is caught with its own name
instead of a bare `INFEASIBLE` (lesson 9.1.2).

Every check must be **sound**: it fires only when no plan can exist, so a scenario that has a plan
never gets a finding. A check compares the least a required project must take with the most a
limit can give.

Write, in `checks.py`, `required(snapshot, scenario)`: each must-do and each forced project with its
window's start years, and each fixed project with only its fixed year. `required` keeps them all: a
required project that is also forced out keeps its window, and a fixed year outside the window is
kept as given, because those are exactly the cases `checks` must report as `no-start`. Then `checks(snapshot,
scenario)`, which returns a list of `(rule, subject)` findings, in this order:

| rule | subject | fires when |
| --- | --- | --- |
| `no-start` | the project | a required project is forced out, or its fixed year is outside its window (then skip its other checks) |
| `alone-over-budget` | the project | no start left to it keeps its own spend within every year's budget |
| `alone-over-crews` | the project | no start left to it keeps its crews (needed in every year of work) within its program's crews |
| `required-over-budget` | the year, as text | the least that the required projects must spend in that year exceeds its budget |
| `required-alternatives` | the group | two or more required projects share a group |
| `floor-out-of-reach` | the region | the capex of every project in the region that is not forced out is below its floor |

The first three come per required project, in id order; then years in order, groups and regions
sorted. A required project's least spend in a year is the minimum over the starts left to it. The
budgets and crews in force are the snapshot's, replaced by the scenario's where it sets them;
`starts`, `spend`, `budgets` and `crews` are given.
