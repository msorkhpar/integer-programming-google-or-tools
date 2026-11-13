The planners who wrote the repair-or-replace model now want to know how strong its LP relaxation is
in each of the two forms Pyomo can write, because a weak bound makes branch-and-bound slow on the
utility's full fleet.

The starter has the model, `build(assets, demand)`, with one `Disjunction` per transformer. Write
`lp_bound(assets, demand, form)` in `bounds.py`: build the model, let the transformation `form`
(`"gdp.bigm"` or `"gdp.hull"`) write the disjunctions as MILP rows, relax every binary to
$`[0, 1]`$ with `core.relax_integer_vars`, solve with `appsi_highs`, and return the objective
`m.total`. `lp_bounds` then returns the pair (big-M bound, hull bound).

Both are lower bounds on the cheapest plan, and the tests check them against each other, against
that optimum, and against their exact LP values. About eight lines.
