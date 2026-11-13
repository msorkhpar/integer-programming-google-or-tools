The crew schedule reached GridCap's reliability engineer:

> Your plan trims C13 in the first five weeks and leaves C12 for weeks 17 to 23. C12 is the one I
> worry about: its trees are growing into the lines, and every week we wait its risk goes up. A
> trim in September does not take out a year of risk; it takes out what is left of the year, and the
> circuit carried the rest. Order the work so that we carry the least risk over the season. And
> a circuit we skip waits half a year more for next season's crews; count that too.

You start from the crew scheduler of the lesson before. Read each circuit's weekly growth of risk,
and have the generator draw it. A circuit carries its weekly share of its yearly risk, plus its
growth for every week it has waited, until its trim ends; a circuit left for next season carries it
until 26 weeks past the season's end. Plan the least risk carried in total, within the budget and
the crews, and report it. A trim that fills the whole season still fits.

**The report.** Only the status line changes: it ends `risk carried $<risk carried>k`, with a
thousands comma, in place of `risk removed $<risk removed>k a year`. `main.py` still sets one worker.

Run executes `main.py`, which plans the tiny season (six circuits of GridCap, a fictional utility,
drawn by `vegcrew/generate.py` from seed 54) and prints the report; `expected/report.txt` is the
report it should print. Submit runs every test in `tests/`, the earlier steps' included, and compares
Run's report with the expected one.
