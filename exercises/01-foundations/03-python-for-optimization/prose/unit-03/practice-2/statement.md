The outage team's validator, `check_request`, is finished: it returns the name of every rule an
outage request breaks. Their test suite runs one parametrized test per row of a table, `CASES`, and
the table is empty. Fill it.

`cases.py` holds the validator, its six rule names in `RULES`, and `BASE`, a valid request (every
value is text, as it arrives from the form). Write `CASES`: a list of six `(row, rule)` pairs, one for
each rule in `RULES`, where `row` is a request that breaks that rule. The rules:

| rule | a request breaks it when |
| --- | --- |
| `hours-not-a-number` | `hours` does not read as a number |
| `negative-hours` | `hours` is below zero |
| `unknown-crew` | `crew` is not one of `CREWS` |
| `week-out-of-range` | `start_week` or `end_week` is outside 1 to 52 |
| `end-before-start` | `end_week` is before `start_week` |
| `priority-out-of-range` | `priority` is not 1 to 5 |

A case is only useful if a broken check makes its test fail, so each row must break its own rule and
no other. Keep weeks whole numbers, since the validator reads them with `int`. Don't change the
validator or `BASE`.

About eight lines.
