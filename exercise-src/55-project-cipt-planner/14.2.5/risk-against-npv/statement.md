The planning lead read the two plans of the lesson before and asked for something in between:

> The NPV plan leaves too much risk on the table, and the risk plan gives up $5.7M of NPV. Show us
> the options in between: for each extra bit of risk removed, how much NPV does it cost? And let us
> set a floor on risk removed and get the best NPV above it.

You start from the planner that values each start by NPV and by risk removed. Give the planners
the frontier: plans from the best NPV to the most risk removed, with plans in between, none of
which is beaten on both goals by another, and where two plans tie on one goal, the one that does
better on the other. Let the export set a floor on risk removed, and plan the best NPV above it.

`cipt/goals.py` already defines `Point`, one frontier plan with its NPV and risk removed. Two
plans whose NPVs differ by at most 0.5 count as the same point, and only the first found is kept;
dominated points are dropped after that. Every NPV in the export is a whole $k.

Run's report gains a section: after the plan, `main.py` prints an empty line, the line
`NPV against risk removed:`, then one line per frontier point of the demo export, from the best NPV
to the most risk removed:
`  NPV $<npv>k  risk removed $<risk>k  funds <ids>`, with two spaces before `NPV` and between the
parts, NPV in whole $k and risk with one decimal (both with thousands commas), and the funded
project ids in id order, separated by a comma and a space.

`cipt/diagnose.py` is the next lesson's stub, as the reference has it; no code of this step
imports it, so leave it as it is.

Submit runs every test in `tests/`, the earlier steps' included, and compares Run's report with the
expected one.
