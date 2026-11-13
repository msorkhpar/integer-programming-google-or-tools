GridCap's vegetation planner now runs the planner every Monday, and wrote:

> I ran the plan twice this morning on the same data, to check something, and got two different plans,
> with different risk totals. Which one did we send the crews? When the regulator asks why C27 waited
> until September, I need to rerun the plan and get the *same* plan, and I need to know that next
> month's code change did not quietly change it.

You start from the planner with overrides and explanations. Make the search repeat: the same season
gives the same plan on every run, on any machine, for one OR-Tools version. Give each plan a record
that names what it was planned from (a fingerprint of the season and the overrides), the solver and
its settings, and what it decided, written one way so two records can be compared as text; and let
the command line print it with `--record`. The tests compare today's records of the tiny and the
small seasons with reviewed golden files in `tests/golden/`.

**`main.py`.** Remove the line that sets `planner.WORKERS = 1`: the planner's settings now repeat the
search by themselves. After the overrides' sections, print an empty line and
`input sha256 <fingerprint>, records of two runs identical: <yes or no>`, where `<fingerprint>` is
the first 12 hex digits of the fingerprint of the tiny season (seed 54) with no overrides, and the
two records are `dumps(plan_record(raw, make_plan(season)))` of two plans of that season made one
after the other in the same process.

Run's report gains that line, as `expected/report.txt` shows. Submit runs every test in `tests/`,
the earlier steps' included, and compares Run's report with the expected one.
