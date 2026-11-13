The crane of the previous practice is booked by a planning master that chooses which lifts to do
this month, $`x_l \in \{0,1\}`$; a scheduling check then tests each chosen month. Every refused
month costs one more master solve. The planners want the master to refuse, by itself, the months
that are obviously too full, with linear rows in $`x`$ that never refuse a month the crane could
really do.

Lift $`l`$ needs $`p_l`$ crane days, may begin on day $`r_l`$ and must end by day $`d_l`$ (one
crane, one lift at a time). Days are counted as in the lesson's half-open windows $`[r, e)`$: the
lift may use the days $`r_l, r_l + 1, \dots, d_l - 1`$, so its window holds $`d_l - r_l`$ crane days,
and a stretch $`[a, b)`$ holds $`b - a`$. Write the rows first: which stretches $`[a, b)`$ get a
row, which lifts each row counts, and the row itself with a label and quantifier. A stretch runs from
some lift's release $`a`$ to some lift's deadline $`b > a`$, and it gets a row only when at least
one lift's whole window lies inside it; a stretch with no such lift gets none. Then write
`add_energy_rows(model, x, lifts)` to add them and return them in a dict keyed by `(a, b)`.
`lifts[name]` is `(days, release, deadline)`; `x[name]` is the master's variable.

The tests fix a month's lifts and ask the solver whether the master allows it, so any correct
formulation passes. About six lines.
