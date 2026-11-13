Finance sent the fourth request:

> **Request 4.** From the next cycle, money a year leaves unspent is not lost: it moves into the next
> year, up to a fifth of one year's budget. It moves forward only. No year may spend next year's
> money.

The change is proposed and archived in `openspec/`: it renames the yearly budget requirement, modifies
it, keeping its two old scenarios, and adds a check of the percent. The specs, the tests (one per
scenario, named after it) and the expected report are given and read-only.

You start from the planner with must-do overrides, where `Request.carry` is a stub field. Let each
plan year but the last pass unspent money to the next, up to the carry-over percent of one year's
budget, never less than nothing, and make each year's budget row a balance of what it spends, passes
on and was passed. A request with no carry-over must plan exactly as before. Refuse a percent
outside 0 to 100, and let the report count what each year passes on from the plan's spend.

Run executes `main.py`, which plans a tiny portfolio: 12 projects of GridCap, a fictional utility,
drawn by `capplan/portfolio.py` from seed 58, over three years with $1,500k a year, a 25% share for
Plains, one must-do and 20% carry-over, and prints a line for every plan year with what it carries;
`expected/report.txt` is the report it should print. Submit runs every test in `tests/`, the earlier
steps' included, and compares Run's report with the expected one.
