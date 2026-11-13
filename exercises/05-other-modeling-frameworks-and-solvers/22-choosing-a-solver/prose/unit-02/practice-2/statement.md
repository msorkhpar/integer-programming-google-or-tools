A team benchmarks solvers by **time-to-gap**: how much work a solver spends before its relative gap
first falls to a target, such as 1%. Each solver's log has been parsed into progress rows, in order:
`(work, incumbent, bound)`, where `work` is the solver's own deterministic count at that moment,
`incumbent` the objective of the best plan found so far, and `bound` the solver's bound on every
plan. The team uses one gap definition for every solver, whatever the solver's log says:

```math
\text{gap} = \frac{|\,\text{bound} - \text{incumbent}\,|}{|\,\text{incumbent}\,|}
```

Write `work_to_gap(progress, target)` in `togap.py`: the `work` of the first row whose gap is at most
`target`, or `None` if no row gets there. Every row has an incumbent, never 0. The logs can come
from maximizations (bound above incumbent) or minimizations (bound below).

About five lines.
