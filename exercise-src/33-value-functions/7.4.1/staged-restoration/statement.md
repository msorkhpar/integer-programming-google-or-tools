A rural electric cooperative serves `customers_served` customers. When a storm takes a line down its
crews rarely restore everyone at once: they switch some customers onto another feeder within minutes,
fix the main line an hour later, and reach the last houses after that. So each outage in the
cooperative's log is a list of restoration **steps**: `Step(customers, minute)` says that `customers`
customers came back on supply `minute` minutes after the outage began. Every customer in an outage
lost power at its start.

Write `indices(outages, customers_served)` in `outages.py`, returning the year's SAIFI, SAIDI and
CAIDI as `{"SAIFI": ..., "SAIDI": ..., "CAIDI": ...}`. The cooperative follows the IEEE rule for
what counts: a customer who is back on supply within five minutes (five included) had a momentary
interruption, which counts in none of the three indices, even when other customers of the same
outage waited much longer. CAIDI is the average wait of an interrupted customer, and 0 in a year with no sustained
interruption.

Work the first test's outage by hand before you code: 600 customers restored at 30 minutes and 400
at 90, out of 10,000 served. How many customer interruptions is that, and how many customer-minutes?

About ten lines.
