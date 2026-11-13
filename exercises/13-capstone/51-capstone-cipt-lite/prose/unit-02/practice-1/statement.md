Milestone 2's solver hands back a plan, and the planning team will not take the solver's word that
it is valid: a wrong row would approve its own plan. You write the checker that reads only the
practice snapshot and the plan, with no model and no solver, and names every row the plan breaks.
Milestone 5's properties will call it on hundreds of plans.

A plan is `{project id: start year}`. Project $`j`$ started in year $`t`$ spends `cost[k]` in year
$`t + k`$ and keeps its `crews` crew-months busy in each of those years; years past the horizon are
not counted. A region's floor is met by the whole cost (`sum(cost)`) of its funded projects.

In `checker.py`, write:

| function | contract | lesson |
| --- | --- | --- |
| `spend_by_year(snap, plan)` | `{year: $k}` for every year of the horizon | 6.4.2 |
| `broken(snap, plan)` | the sorted names of every broken row, `[]` for a valid plan | 12.3.2 |

| row | broken when | lesson |
| --- | --- | --- |
| `window_J1` | J1's start is outside `earliest`..`latest` | 6.4.1 |
| `must_J1` | J1 is must-do and not in the plan | 6.5.1 |
| `alt_G1` | two or more projects of group G1 are in the plan | 6.5.3 |
| `after_J2_2028` | J2 starts in 2028 and its parent is not in the plan, or started later than 2028 minus J2's lag | 6.5.2, 6.5.4 |
| `budget_2028` | the plan spends more than the 2028 budget | 6.4.2 |
| `region_South_2028` | the plan's South projects spend more than South's 2028 budget | 6.5.5 |
| `crews_lines_2028` | the `lines` projects at work in 2028 need more crew-months than 2028 has | 6.4.2 |
| `floor_North` | the whole cost of the funded North projects is below North's floor | 6.5.5 |

A limit equal to the use is met. A region missing from `region_budget`, a program missing from
`crews` and a region missing from `floor` have no limit of that kind: no row, so nothing to break.
About forty lines.
