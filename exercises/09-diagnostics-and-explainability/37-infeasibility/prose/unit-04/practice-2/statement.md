A port's harbour master builds next week's berth schedule. Each vessel must berth on exactly one
day inside its window (`first` to `last`, days numbered from 1), and each day has a number of free
berths. Each shipping line has also asked for one day (`wanted`). Those requests are the soft
rules: the harbour master may refuse one, and the vessel then berths on another day of its window,
but a vessel is never sent away. Refusals annoy customers, so the plan must refuse as few requests
as possible. Every refusal counts the same.

Write the formulation first: a 0/1 variable per vessel and day of its window (days in `berths`
only), a 0/1 "refused" variable per vessel, the rows that make every vessel berth once and keep
each day within its berths, an elastic request row per vessel that the refusal variable relaxes,
and an objective that counts refusals. Then write `fewest_refusals(vessels, berths)` to build it
with MathOpt and solve it with HiGHS at a relative gap of 0
(`mathopt.SolveParameters(relative_gap_tolerance=0.0)`), so the number of refusals is a proven
least, as in the lesson's own solves.

`vessels` maps a name to `(first, last, wanted)`; `berths` maps a day to its free berths. Return
`(refused, schedule)`: the sorted names of the refused vessels, and a dict giving the day each
vessel berths. When several answers refuse equally few, any of them is right: the tests check the
number of refusals and that the schedule keeps every rule. About fifteen lines.
