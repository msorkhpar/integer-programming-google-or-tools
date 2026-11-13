Engineering sent the fifth request:

> **Request 5.** The cap of three starts a year was the design-review board's capacity. Reviews are
> now done as each design is ready. Retire the cap. And make sure nobody who still sends it gets a
> different plan without being told.

The change is proposed and archived in `openspec/`: it removes the Yearly start cap requirement, with
its reason and migration, and adds two requirements for what replaces it. The specs, the tests (one
per scenario, named after it; the removed scenario's test is gone) and the expected report are given
and read-only.

You start from the planner with carry-over. Take the yearly start cap out of the model, so any number
of projects may start in a year. Keep the request's field, with no cap as its default, and refuse,
before solving, any request that still sets it, with a message that names the change that retired it.

Run executes `main.py`, which plans a tiny portfolio: 12 projects of GridCap, a fictional utility,
drawn by `capplan/portfolio.py` from seed 58, over three years with $1,500k a year, a 25% share for
Plains, one must-do and 20% carry-over, prints the plan, then what happens to the same request with a
start cap of 3, and the line about the specs; `expected/report.txt` is the report it should print.
Submit runs every test in `tests/`, the earlier steps' included, and compares Run's report with the
expected one.
