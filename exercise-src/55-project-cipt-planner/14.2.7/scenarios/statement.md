Planning season starts, and the requests multiply:

> Finance wants to see the plan with $2.76M held back in 2029. P028 is waiting for a permit, so
> show us the plan without it. The board wants the Valley rebuild P030 in. We need all of these side
> by side, against the same export, and in six months we need to know exactly what each run was
> planned from and what it said.

You start from the planner with diagnostics. Add scenarios: a named set of budget changes and
overrides (projects forced in, forced out, or fixed to a start year) kept as data beside the
export, never written into it. Each override becomes a named row, so a conflict can name it. Two
plans are compared by the projects selected, deferred and shifted. Store each export once, as a
snapshot under the hash of its content, refuse a stored snapshot whose content no longer matches
its hash, and store each run with the snapshot it was planned from, in one SQLite file.

The canonical form of an export is its JSON with sorted keys and no spaces after `,` and `:`; the
snapshot's hash is the sha256 hex digest of that text in UTF-8. Saving a scenario under a name that
is already stored replaces it, and the runs of a scenario come back as `Plan`s, oldest first.

Run's report gains a section: `main.py` now compares the demo plan with a scenario named
`more money` that adds $1,000k to the budgets of 2028 and 2029. After the frontier section it
prints an empty line, then `scenario more money: NPV $<base npv>k -> $<scenario npv>k` (whole $k,
thousands commas), then `  selected <ids>; deferred <ids>` with the ids joined by a comma and a
space, or `none`, then one line `  shifted <id> <base start> -> <scenario start>` per project that
starts in another year.

`cipt/trust.py` holds the next lesson's stubs, as the reference has them; no code of this step
imports it, so leave it as it is. Submit runs every test in
`tests/`, the earlier steps' included, and compares Run's report with the expected one.
