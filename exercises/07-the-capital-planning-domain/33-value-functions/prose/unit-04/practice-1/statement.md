A water utility plans when to renew its mains. Each main may start in one or more years, and the
model has a binary start variable `x[(main, year)]` for each. For every possible start the asset
team has computed three benefits in `benefits[(main, year)]`: breaks avoided, leakage avoided in
megalitres, and NPV in $k. The board has fixed a reference swing and a weight for each measure, and
it wants every number in the plan's report in **$k of NPV-equivalent**: the NPV that would earn the
same value.

Write `coefficients(benefits, reference, weights)` in `renewals.py`, returning each start's value in
$k of NPV-equivalent, and `objective(x, coefficient)`, the plan's value as one MathOpt linear
expression in the start variables. The tests read the objective on fixed plans with
`mathopt.evaluate_expression`; nothing is solved.

The measures' keys, the same in `benefits`, `reference` and `weights`, are `"breaks"`, `"leakage"`
and `"npv"`; the financial measure, the one that sets the dollar conversion, is `"npv"`.

Write $`v_{i,t}`$ in the notation of lesson 7.4.4 first, then the factor that turns it into dollars.
The references are the board's, fixed for the planning cycle: a new candidate must not change any
other main's value. About six lines.
