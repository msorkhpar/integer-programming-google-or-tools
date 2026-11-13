The plans are trusted, and finance sent the last request:

> **Request 8.** Finance wants the plan as a table they can read: money and risk by year, against
> each year's budget, with a line saying how good the plan is. The operations analysts will run it
> themselves, so it needs a command, a version, and tests that tell them when a change has moved the
> answer. Same input, same report, every time.

You start from the model with scenarios. Write the plan as finance reads it: one line per plan year,
years with no work included, with its units, replacement cost, outages and their cost, total, budget
and the risk removed; then a Markdown report of those lines, their totals, and a sentence giving the
solver's status and the bound no plan beats. Put it behind a command, `renewal`, that writes the
report to a file or prints it, and give the package a version that matches `pyproject.toml` (given,
read-only). The report for a 30-unit fleet must match the reviewed golden file in `tests/golden/`.

Run executes `main.py`, which runs the command's `main` on a tiny fleet: 25 transformers of GridCap,
a fictional utility, drawn by `renewal/fleet.py` from seed 56, with a budget of $2,000k a year and
the command's default gap, and prints the finance report. Its whole body is one call:

```python
sys.exit(main(["--units", "25", "--seed", "56", "--budget", "2000"]))
```

with `main` from `renewal.cli`. The report it prints, like the golden file, is Markdown:

```text
# Transformer renewal plan, <first year>-<last year>

Fleet of <units> transformers (fictional data). All money in $k.

| Year | Units | Replacement | Outages | Outage cost | Total | Budget | Risk removed |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| <year> | <units> | <replacement> | <outages> | <outage cost> | <total> | <budget> | <risk removed> |
| Total | <units> | <replacement> | <outages> | <outage cost> | <total> | <budget> | <risk removed> |

Solver status <status>. No plan under these rules removes more than $<bound>k; this one is within <gap> of that bound.
```

with one `<year>` row per plan year, years with no work included, and a blank line after the title,
after the fleet line and after the table. Money has a comma between thousands and no decimals;
units and outages are plain counts. The Total row sums each column, the budget too. `<gap>` is
(bound − value) / bound as a percentage with two decimals (`f"{gap:.2%}"`, 0 when the bound is 0).
`expected/report.txt` is the report it should print. Submit runs every test in `tests/`, the
earlier steps' included, and compares Run's report with the expected one.
