A fictional utility's planning database sends its portfolio export to CIPT Lite as text: one row per
project and one per yearly budget, every cell a string, the way `csv.DictReader` hands them over.
This cycle's export has six defects planted in it. Your reader must refuse it, find all six, and
accept a clean export as the snapshot every later milestone uses.

**The rows.** `export["projects"]` holds rows with the columns `id`, `program`, `region`, `cost`
(the yearly amounts in $k joined by `;`), `earliest`, `latest`, `must` (`"0"` or `"1"`), `parent`
(an id, or `""`), `lag`, `group` (an alternative group, or `""`) and `crews`. `export["budgets"]` holds
`year` and `amount`. `export["years"]` (a list of ints) and `export["rate"]` (text) are given.

**The snapshot** you build is the practice series' format, restricted to what this export carries:

```python
{"years": [2027, 2028, 2029], "rate": 0.05, "budget": {2027: 400, ...},
 "projects": {"J1": {"program": "lines", "region": "North", "cost": [200, 100], "earliest": 2027,
                     "latest": 2028, "must": True, "parent": None, "lag": 0, "group": None, "crews": 2}, ...}}
```

A project started in year $`t`$ spends `cost[k]` in year $`t + k`$, so its start years are
$`T_j = \{e_j, \dots, l_j\}`$, and every one of them must leave room for the whole profile inside the
horizon.

In `export.py`, write the two stages (`review`, which runs them in order, and `rejected` are given).
Each finding is a tuple `(severity, rule, subject)`.

| function | contract | lesson |
| --- | --- | --- |
| `read_rows(export)` | `(snapshot, [])` for clean cells; otherwise `(None, findings)` with **every** cell problem of every row | 1.3.2, 12.2.1 |
| `cross_rules(snapshot)` | the findings of the three rules below, on a snapshot whose cells are clean | 12.2.2 |

Cell rules (all errors). A budget row whose `year` is not a whole number (`"2O28"`) is a
`bad-budget` with that text as its subject, and the year it was meant for then has no budget, so it
also gets a `missing-budget`:

| rule | subject | fires when |
| --- | --- | --- |
| `not-a-number` | `J2.cost`, `J2.earliest`, ... | a cost amount is not a whole number above 0 (one finding for the whole `cost` cell, however many of its amounts are bad), or `earliest`, `latest`, `lag`, `crews` is not a whole number |
| `unknown-code` | `J3.region`, `J3.program`, `J3.must` | a program other than `lines`/`poles`, a region other than `North`/`South`, a `must` other than `0`/`1` |
| `empty-window` | the id | not $`y_0 \le e_j \le l_j`$ with $`l_j + n_j - 1 \le y_{\text{last}}`$, where $`n_j`$ is the number of amounts in the `cost` cell; checked whenever `earliest` and `latest` are whole numbers, even if an amount of `cost` is bad |
| `unknown-parent` | the child's id | the parent names no project of the export |
| `bad-budget` | the row's `year` cell, as written | its `year` or its `amount` is not a whole number, or the amount is below 0 |
| `missing-budget` | the year, as text | a horizon year with no budget row that was read, unless a `bad-budget` finding already has that year as its subject |
| `duplicate-id` | the id | a second row with an id already read (that row is then skipped) |

Cross-project rules:

| rule | subject | fires when | severity |
| --- | --- | --- | --- |
| `parent-cycle` | the ids on the cycle, sorted, joined with `+` | following parents from a project leads back to it | error |
| `parent-too-late` | the child | the parent's earliest start plus the lag is after the child's latest start | error for a must-do child, warning otherwise |
| `must-spend-over-budget` | the year, as text | the least that must-do work can spend in the year, each must-do at its cheapest start for that year, exceeds the year's budget | error |

The cross rules read parents and costs as numbers and ids, so they run only once every cell is
clean: an export with cell problems is refused on those alone, and its next version is checked again.
Errors reject; a warning alone does not, and `review` then returns the snapshot. About seventy lines.

The practice simplifies the lesson's reader and gate: one cell rule, `not-a-number`, stands for the
lesson's `not-a-whole-number` and `below-minimum`, and the gate has three rules
instead of four (the lesson's `two-must-do-alternatives` is left out).
