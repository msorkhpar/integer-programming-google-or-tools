The planning lead's first request:

> We have $38.39M of capital for the next five years and 40 candidate projects on GridCap small.
> Tell us which to fund to get the most value. Use the NPV finance quoted for each project.
> We'll worry about years later.

The project you start from is the skeleton: it reads the export and prints a report, but its model
is empty and `solve` funds nothing. Make the planner decide. Each project is a yes-or-no choice, the
funded projects together may cost no more than the capital budget, and the plan has the most total
value. Solve the model with HiGHS through MathOpt, keep anything HiGHS prints out of the report, and
read the answer back as a `Plan` in which each funded project starts in its earliest year.

The command line, `python -m cipt EXPORT.json`, plans the export file it is given.

`cipt/solve.py` already imports MathOpt and holds stubs for `run_highs` and `read_plan`; write
their bodies and make `solve` use them. `cipt/report.py` needs no change. It prints the report in
this format, every amount in whole $k with thousands commas:

- `<request name>: <status>`;
- `funded <n> of <all> projects, capex $<capex>k of $<capital budget>k, value $<value>k`, where
  capex and value are the totals of the funded projects;
- one line per funded project, in id order: two spaces, the id, two spaces, `start <year>`, two
  spaces, `capex` and a space and the capex right-aligned in 6 characters, two spaces, `value` and
  a space and the value right-aligned in 6 characters, two spaces, the project's name.

Run executes `main.py`, which plans the demo export in `data/demo.json` (GridCap tiny, a fictional
utility) and prints the report; `expected/report.txt` is the report it should print. Submit runs
every test in `tests/`, the skeleton's own included, and compares Run's report with the expected one.
