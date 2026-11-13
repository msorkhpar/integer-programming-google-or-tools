A hospital plans its equipment replacements over a few years. Each item is installed in one year,
pays its whole `cost` ($k) in that year and needs `engineer_days` of the biomedical engineers'
time in that year. It may be installed in any plan year from its `release` year to its `deadline`
year. Items marked `required` must be installed. An item may name another it `excludes` (the two
need the same room, so at most one is installed). The finance office gives a `budget` per year and
the engineering office `engineers` (days available) per year, both keyed by the plan's years.
Each department has a `dept_minimum`: the least the plan must spend on that department in total.

Before the hospital's model is ever solved, the planners want the input checked for five known
causes of "no plan":

| Check | Subject | The cause |
| --- | --- | --- |
| `"window"` | the item | a required item has no plan year in its window |
| `"budget"` | the item | a required item costs more than the budget in every year it may use |
| `"engineers"` | the item | a required item needs more engineer-days than are available in every year it may use |
| `"exclusion"` | both items' names, sorted, joined by `"\|"` | two required items exclude each other |
| `"minimum"` | the department | a department's minimum is more than all its items together cost |

The plan years are the keys of `budget`; `engineers` has the same keys. For the `"minimum"` check,
"all its items together" means every item of the department, required or optional, whatever its
window. (Leaving out an item whose window misses every plan year is sound too, and the tests accept
either.)

Write `precheck(items, budget, engineers, dept_minimum)` returning the sorted list of
`(check, subject)` pairs, each pair once. Every check must be **sound**: it may fire only when no
plan can exist, so a program with a plan always gets `[]`. Work out, for each check, which
quantity has to be the least possible demand and which the most possible supply.
About twenty-five lines.
