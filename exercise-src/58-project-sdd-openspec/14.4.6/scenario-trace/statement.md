GridCap's auditors sent the sixth request:

> **Request 6.** For every rule in these specs, show us the test that proves the planner keeps it. For
> every test, show us the rule it checks.

The change is proposed and archived in `openspec/`: it adds a traceability requirement to the
checker's spec, with the naming convention every test already follows. It also finishes the open
tasks of the must-do change, whose scenario "A must-do that cannot start in the plan is refused" has
been in the living spec with no test and no code. The specs, the tests and the expected report are
given and read-only.

You start from the planner without the start cap, where `specs_check.trace` is a stub. Write the
trace: every scenario of the living specs to the test named after it in its capability's test file,
and every test of those files to its scenario, reporting both kinds of gap. Then make the planner
refuse, before solving, a must-do project that cannot start in any plan year, naming it, where it
now returns an infeasible plan with no word about why.

Run executes `main.py`, which plans a tiny portfolio: 12 projects of GridCap, a fictional utility,
drawn by `capplan/portfolio.py` from seed 58, prints the plan, the refusal of the retired start cap,
the line about the specs, and a last line with the trace; `expected/report.txt` is the report it
should print. Submit runs every test in `tests/`, the earlier steps' included, and compares Run's
report with the expected one.
