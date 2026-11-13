A water district chooses which booster stations to build; that is the master's decision,
$`x_j \in \{0,1\}`$. Once the stations are fixed, it pumps the cheapest way it can: station $`j`$
delivers up to its capacity $`u_j`$ at an energy cost $`e_j`$ per megalitre, and water bought from
the neighboring district costs $`p`$ per megalitre, at most $`L`$ megalitres. The district must
deliver its demand $`D`$, and every station built also needs $`r_j`$ megalitres to fill its own
tank. Pumping and buying are continuous: this is the subproblem.

Write the subproblem for a fixed plan $`\hat x`$ first: its variables with their bounds, its
objective, and each row with a label, with every row's right-hand side written as a function of
$`\hat x`$. Then write the optimality cut it gives: the expression in the master's $`x`$ that
equals the pumping cost at $`\hat x`$ and is at most the pumping cost at every other plan.

Then write `pumping_cut(stations, demand, limit, price, plan, x)` to build and solve the
subproblem with GLOP for `plan` (a dict from station name to 0 or 1) and return
`(cost, cut)`: the optimal pumping cost and the cut, as a MathOpt linear expression in the master
variables `x` (a dict from station name to variable). `stations[j]` holds `"capacity"`,
`"energy"` and `"refill"`. The tests only call plans for which the subproblem is feasible.

About fifteen lines.
