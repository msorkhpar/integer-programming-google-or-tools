The planners sent the third request:

> **Request 3.** Some projects have to be done whatever the model thinks they are worth: a
> regulator's order, storm damage, a safety finding. Give us a must-do switch. And every must-do
> needs a written reason, or the auditors will ask us who forced what, and why.

The change is proposed and archived in `openspec/`, and the living capital-plan spec states its
requirements. The specs, the tests (one per scenario, named after it) and the expected report are
given and read-only. One scenario of the change has no test yet; it is not part of this step.

You start from the planner with the regional share, where `Request.must_do` is a stub field and
`report.overrides` a stub. Make every must-do project start in some year of its window, chosen by the
model, without touching its value. Refuse, before solving, an override for a project not in the
portfolio, or with no reason. List each override with its reason in the report.

Run executes `main.py`, which plans a tiny portfolio: 12 projects of GridCap, a fictional utility,
drawn by `capplan/portfolio.py` from seed 58, over three years with $1,500k a year, a 25% share for
Plains and one must-do project, and prints the plan, its overrides, each year's line and the line
about the specs; `expected/report.txt` is the report it should print. Submit runs every test in
`tests/`, the earlier steps' included, and compares Run's report with the expected one.
