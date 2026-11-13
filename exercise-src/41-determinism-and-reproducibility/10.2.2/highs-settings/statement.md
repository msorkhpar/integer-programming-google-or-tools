A freight company plans next week's truck loads with a MILP solved by HiGHS through MathOpt, every
night, and wants each night's run to be repeatable from its manifest. The manifest records three
numbers: a seed, a thread count and a node limit.

Write `highs_parameters(seed, threads, nodes)` that returns the `mathopt.SolveParameters` for such a
run: the seed, a pinned thread count passed the way HiGHS accepts it through MathOpt, and the node
limit as the only limit you add. Set no time limit, since a clock limit stops at a different point
on every run. Leave the gap tolerances at their defaults: the reference sets nothing besides these
three, and the gap is not set to 0. The tests solve a small model with what you return, always with
`threads=1`.

About five lines.
