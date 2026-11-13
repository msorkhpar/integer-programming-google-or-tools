GridCap's vegetation program manager sent the first request:

> We have $962k for tree trimming this year and twenty distribution circuits that are due. Tell me
> which ones to trim so that we take out the most tree risk. I don't need dates yet, just the list.

You start from the skeleton: it generates a season, reads it into a `Season` and prints a report,
but `make_plan` trims nothing. Make the planner decide. Each circuit is trimmed or not, the trimmed
circuits together cost no more than the season's budget, and the plan removes the most risk a year.
Build the model with MathOpt, solve it with HiGHS with no gap left between the plan and its bound,
and read the answer back as a `Plan` with one `Trim` per trimmed circuit, the total cost and the
total risk removed. A budget too small for any circuit is still an answer: an optimal plan with no
trims.

The report is already written: `vegcrew/report.py` prints the season line, the status line and one
line per trimmed circuit, and this step does not change it.

Run executes `main.py`, which plans the tiny season (six circuits of GridCap, a fictional utility,
drawn by `vegcrew/generate.py` from seed 54) and prints the report; `expected/report.txt` is the
report it should print. Submit runs every test in `tests/`, the skeleton's own included, and compares
Run's report with the expected one.
