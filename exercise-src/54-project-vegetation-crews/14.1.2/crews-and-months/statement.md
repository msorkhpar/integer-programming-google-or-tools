The program manager sent the list to the crew supervisor, who answered:

> Your list needs 45 crew-weeks of trimming. I have two crews from April to September, and I plan
> them a month at a time: each crew gives me four weeks a month. Tell me which circuits to trim *and
> in which month*, without ever booking more work in a month than my crews can do.

You start from the knapsack of the lesson before. Read each circuit's crew-weeks and the season's
crews and months, and have the generator draw them. Let the model choose the month of each trimmed
circuit, trim a circuit in one month at most, and keep each month's booked crew-weeks within what
its crews can do, as well as the season within its budget. Keep anything HiGHS prints out of the
report. The report shows each month's booked crew-weeks against its capacity. A season of one month
is a season too: its crews may stop a trim the budget allows.

**The report.** The first line gains `, crews <crews>, months <months>`. After the status line comes
one line per month, from month 1 to the last, an empty month included: two spaces, `month <m>: `, the
crew-weeks booked that month right-aligned in two characters, `/`, the month's capacity and
` crew-weeks`; then, only when the month has trims, two spaces and the trims sorted by circuit id,
each as `<cid>(<weeks>)`, one space apart. An empty month's line ends at `crew-weeks`, so no line ends
in a space.

**Which months.** The objective counts the risk removed whatever the month, so the tiny season has
several equally good plans, and the months HiGHS returns depend on the order the model is built in
(the lesson shows the same model built in two orders giving two plans). `expected/report.txt` comes
from this order: the variables circuit by circuit in the season's order, months 1 to the last within
each circuit; then the once rows in circuit order, the crew rows in month order, the budget row, and
the objective, solved with HiGHS at a relative gap of zero. Build yours in that order for the report
check; the tests accept any order.

Run executes `main.py`, which plans the tiny season (six circuits of GridCap, a fictional utility,
drawn by `vegcrew/generate.py` from seed 54) and prints the report; `expected/report.txt` is the
report it should print. Submit runs every test in `tests/`, the earlier steps' included, and compares
Run's report with the expected one.
