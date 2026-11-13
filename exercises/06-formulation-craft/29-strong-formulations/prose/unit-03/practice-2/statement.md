A distribution company (not GridCap) must replace a feeder's wooden poles within four years. The
poles are identical: same age, same type, same risk. Replacing one in year $`y`$ costs $`c_y`$; at
the end of each year, every pole not yet replaced adds a risk cost $`r_y`$; and the crew can replace
at most $`K_y`$ poles in year $`y`$. Every pole must be replaced by the end of the last year.

A first draft, `build_named` in `poles.py`, gives each pole a name: $`x_{p,y} = 1`$ if pole $`p`$ is
replaced in year $`y`$. With 30 poles and four years that is 120 binaries, and every plan appears
once for each way of handing its yearly numbers to the 30 named poles.

Write `build_counted(poles, cost, risk, crew)`: the same plans, with the poles counted instead of
named. It returns `(model, n)`, where `n` maps each year to its one variable. Before coding, write
the formulation: each variable's domain and bounds, the row that says every pole is replaced, and
the objective, in which the number of poles still waiting at the end of year $`y`$ is an expression
in your variables. Check on paper that a plan of the named model and its counts have the same cost.

The tests fix the counts of whole plans and ask whether each is allowed and what it costs, and
compare your best plan with the named model's. About six lines.
