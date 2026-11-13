A city transit agency is replacing diesel buses. Its planning model, already written, answers one
question at a time: given a floor on tonnes of CO2 cut per year, which replacement plan carries the
most riders? It is wrapped for you as `solve_at(floor)`, which returns the plan's score as a pair
`(riders, tonnes_cut)`, or `None` when no plan cuts that much.

The agency wants to show its board the plans between "most riders" and "most CO2 cut". Write
`sweep(solve_at, low, high, n)` in `sweep.py`. It asks `solve_at` at `n` floors evenly spaced from
`low` to `high` (both included, `n >= 2`), in increasing order, and returns the list of different
scores it got back, in the order first found. A floor that returns `None` adds nothing.

The tests pass their own `solve_at`, which records every floor it is asked about. About eight lines.
