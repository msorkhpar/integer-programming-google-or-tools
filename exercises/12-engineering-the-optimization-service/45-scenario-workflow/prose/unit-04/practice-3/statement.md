Riverbend Water's (invented for this practice) finance team does not read which mains moved
between two runs; it reads which years' spend changed. Runs are stored as in this lesson, one
`run_start` row per funded main, and a `cost` table holds each main's cost in each year of work
(`year_offset` 0 is the start year).

Write the query `SPEND_DIFF` in `spend.py`. With the named parameters `:a` and `:b` (two run ids) it
returns one row `(year, a_spend, b_spend)` for every calendar year in which the two runs spend
different totals, ordered by year. A run that spends nothing in a year counts as 0 there, and a
year in which the runs spend the same is left out. `spend_diff` already runs the query.

Write the spend of each run in each year first (which pairs of a run's start row and a cost row
land in year $`y`$?), then compare the two runs year by year. About twelve lines of SQL. If you use
`FULL OUTER JOIN`, it needs SQLite `3.39.0` or later; the runner's library is `3.46.1`.
