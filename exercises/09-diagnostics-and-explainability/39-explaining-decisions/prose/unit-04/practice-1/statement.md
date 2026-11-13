A transit agency's fleet-replacement optimizer stores each run as a record, and its finance office
wants a short version of every run in its own terms. A record is a dictionary with `"budget"` and
`"spend"` (each `{year: $k}`), `"npv"` (the plan's NPV, $k), `"bound"` (the solver's proven limit on
the best NPV, $k) and `"status"` (the solver's termination, such as `"OPTIMAL"` or `"FEASIBLE"`).

In `fleet_finance.py`, write `finance_text(record)`, returning the lines of the finance version, every
number taken from the record:

- one line per year, oldest first: `"2027: spend 10,850 of 11,000, 150 left"`, or, when spend is above
  the budget, `"2027: spend 11,200 of 11,000, OVER by 200"`;
- then one line for the value: `"NPV $30,412k, proven optimal"` when the run is proven, otherwise
  `"NPV $29,950k, not proven: no plan is worth more than $30,600k"`.

Amounts use thousands separators; NPV and bound are rounded to whole $k. Budget and spend may be
floats (a solver's spend is a sum of floats): round each to a whole $k first, then compare and
subtract the rounded amounts, so 10,849.6 of 11,000.0 reads `spend 10,850 of 11,000, 150 left`. Write `proven(record)` first:
a run is proven when its status is `"OPTIMAL"` *and* its bound is within 0.5 of its NPV. Before
coding, say in one sentence why the status alone is not enough. The tests use their own runs.
