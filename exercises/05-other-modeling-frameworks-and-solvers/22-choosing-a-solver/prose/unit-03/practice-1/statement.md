A team at a gas network wants to try commercial solvers on their free tiers before asking for
quotes, and needs to know which of its models each free tier accepts. Free tiers cap model size in
different ways: some cap variables and constraints separately, some cap their sum, and some have
tighter caps when the model has quadratic terms.

A tier is described as `{"linear": caps, "quadratic": caps}`, where `caps` is a tuple
`(max_vars, max_rows, max_sum)`, and any of the three may be `None`, meaning that count is not
capped. A model fits when its variables are at most `max_vars`, its rows at most `max_rows`, and
variables plus rows at most `max_sum`, using the `"quadratic"` caps when the model has quadratic
terms and the `"linear"` caps otherwise.

Write `fits(n_vars, n_rows, quadratic, tier)` in `tiers.py`. About five lines.
