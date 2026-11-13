The risk-ordered schedule went to the field, and three answers came back the same day:

> **Crew supervisor:** The River circuits run through bottom land. Until the ground dries, around week
> 8, we can't get bucket trucks in. And K1 is at training in weeks 10 and 11; K2 is held back for storm
> duty in weeks 14 to 17.
>
> **Environmental lead:** About half of the Hills circuits cross nesting habitat. No work there from
> week 6 to week 13.
>
> **Compliance:** C05 and C16 are overdue on their trim cycle. They are not optional this year.

The supervisor speaks of the small season's two crews. The generator gives K1 the training weeks
10 and 11 in every season and, when a season has more than one crew, gives its last crew the storm
duty in weeks 14 to 17: K2 in the small season, K6 in the medium; the tiny season's one crew has
only the training weeks.

You start from the risk-ordered scheduler of the lesson before. Read three calendars, and have the
generator draw them: each circuit's access windows, each crew's weeks off, and the circuits that
must be trimmed this season. A trim lies wholly inside one window of its circuit, never across the
closed weeks between two; a circuit whose windows are all too short for its trim waits for next
season; no crew works in its weeks off; every must circuit is trimmed, and a season whose musts
cannot all be trimmed is infeasible. The report marks each crew's weeks off.

**The report.** Each crew's week chart marks the crew's weeks off with `x` (a trim never covers
one); the rest of every line is as before.

Run executes `main.py`, which plans the tiny season (six circuits of GridCap, a fictional utility,
drawn by `vegcrew/generate.py` from seed 54) and prints the report; `expected/report.txt` is the
report it should print. Submit runs every test in `tests/`, the earlier steps' included, and compares
Run's report with the expected one.
