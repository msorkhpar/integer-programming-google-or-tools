The crew supervisor booked the month plan and came back within a day:

> Month 1 says C12, 7 crew-weeks, out of 8. That means both my crews on C12 for three and a half
> weeks each. I don't split a circuit between crews: the crew that starts a circuit finishes it, one
> week after another, and it hands nothing over. And C12 takes one crew seven weeks, so it can't sit
> inside one month anyway. Give me a crew and a start week for every trim.

You start from the month planner of the lesson before. Plan in weeks with CP-SAT instead: each
trimmed circuit gets one crew and a run of consecutive weeks as long as the circuit's crew-weeks,
inside the season, and no crew works two circuits in the same week. The budget still holds and the
plan still removes the most risk. A trim may run across a month's end, and a circuit too long for
the season is left out, never shared between crews. The report draws one line per crew, a character
per week.

**The report.** The first line ends `, crews <crews>, weeks <weeks>` in place of the months, the
weeks being the months times 4. The month lines go. After the status line comes one line per crew,
K1 first: two spaces, the crew id, one space, the week chart, two spaces, and the crew's trims in
order of first week, each as `<cid>:<first>-<last>` with both weeks included, one space apart. The
chart has one character per week of the season: `.` while the crew is free, and the last character
of the circuit id while it trims. The two spaces after the chart are printed even for a crew with
no trims, so an idle crew's line ends in two spaces, here and in every later step.

**Which order.** The objective counts the risk removed whatever the order of the work, so the tiny
season has several equally good plans, and the one CP-SAT returns depends on how the model is built
and on how many workers search (the lesson shows the same model, built from the circuits in reverse
order, giving another plan). `expected/report.txt` comes from one worker and this build order: for
each circuit in the season's order that fits, and for each crew from K1 on, the presence literal,
the start and the optional interval, then that circuit's at-most-one; after every circuit, one
no-overlap per crew from K1 on, the budget row, and the objective. Keep `TIME_LIMIT = 10.0` and
`WORKERS = 4` in `planner.py`, and have `main.py` set `planner.WORKERS = 1` (after
`from vegcrew import planner`) before it plans, as the lesson's `main.py` does. The tests accept any
order.

Run executes `main.py`, which plans the tiny season (six circuits of GridCap, a fictional utility,
drawn by `vegcrew/generate.py` from seed 54) and prints the report; `expected/report.txt` is the
report it should print. Submit runs every test in `tests/`, the earlier steps' included, and compares
Run's report with the expected one.
