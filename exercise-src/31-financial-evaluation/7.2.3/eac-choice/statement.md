A water utility (invented for this practice) can keep a pumping station running in several ways:
rebuild it, overhaul it, or patch it. Each option has a price now, a running cost at the end of each
year, and a life in years, after which the utility would do the same thing again. The options last
different numbers of years. `present_cost` in the file values one option today.

Write `yearly_cost(price, running, life, rate)`, the level payment at the end of each year of the
option's life that has the same present value as the option, and `cheapest(options, rate)`, which
returns the name of the option with the lowest yearly cost. `options` maps a name to
`(price, running, life)`. The rate can be zero.

Write the yearly cost as a formula first, and check what it becomes at a zero rate. About eight lines.
