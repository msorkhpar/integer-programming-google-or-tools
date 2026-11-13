The maintenance crew's planners (jobs worth $`v_j`$, crew-weeks $`h_{j,q}`$ per quarter, capacity
$`C_q`$, and pairs $`(a, b)`$ meaning job $`b`$ only with job $`a`$) now get a quick selection from a
GPU MILP solver each night, to hand to their CPU solver as a start. The GPU solver's plans change
from run to run, and its status line says `FeasibleFound` whether or not the plan is any good, so
nothing it reports is taken on trust.

Write `accept(x, reported, bounds, values, hours, capacity, requires, gap)` in `check.py`, returning
`(accepted, reason)`. `x` is the solver's vector of values, `reported` the objective it reported,
and `bounds` the upper bounds on the best possible worth proved by every solver that ran (this is a
maximisation). Check, in this order, and return the first failure:

1. every value within $`10^{-5}`$ of a whole number, else `"not integral"`;
2. round `x` once it passes that check, and judge the rounded plan from here on: values a hair off a
   whole number count as that whole number;
3. each quarter's crew-weeks, from the rounded plan, within $`C_q`$ (to $`10^{-6}`$), else
   `"over capacity in quarter <q>"`, with quarters numbered from 1;
4. each dependency kept by the rounded plan, else `"job <b> without job <a>"`;
5. the rounded plan's own worth, computed from the plan (not `reported`), within `gap` of the
   tightest bound, relatively (divided by the bound), else `"outside the gap"`.

Otherwise return `(True, "accepted")`. About fifteen lines.
