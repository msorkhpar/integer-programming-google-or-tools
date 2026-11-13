A city transit agency upgrades bus stations: upgrade $`i`$ costs `costs[i]` and delivers
`values[i]` (both whole $k), and each is done whole or not at all. The upgrades listed in `must`
(indices) are required by an accessibility ruling and are in every plan. The board will choose
the year's budget from a short list, and wants the best total value at each budget on it.

Write the formulation first for one budget $`B`$: the variables with their domains, the
objective, and each rule as a labelled constraint with its quantifier. Then write
`sweep(costs, values, must, budgets)`, which returns a list of `(budget, value)` pairs in the
order of `budgets`. `value` is the best total value at that budget, as an `int`, or `None` when no
plan meets the rules within it. Solve one MathOpt model per budget with HiGHS, at
`relative_gap_tolerance=0.0`.

The tests compare your values with every plan checked by hand, so any correct formulation passes.
About twelve lines.
