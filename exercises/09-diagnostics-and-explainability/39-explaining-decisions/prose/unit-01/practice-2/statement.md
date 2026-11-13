A school district funds its summer repair jobs from a capital fund and an asphalt fund, with a
fixed number of crew-weeks and one roofing crew. The district's optimizer has chosen this summer's
jobs, and every limit has some room left except the roofing crew. The facilities manager asks
which limits are really holding the plan back: whole jobs cannot use the last few dollars or
crew-weeks, so a limit with room left can still be the reason a job was not added.

Each limit is a `Limit` with a name, how much of it each job uses (`use`; a job not listed uses
none) and its cap. A plan is the set of chosen jobs. In `refusals.py`, write:

- `refusals(limits, plan, candidates)`: for each candidate job, the names of the limits that would be
  over their cap if that one job were added to the plan, sorted by name. A limit filled exactly to
  its cap is not over it.
- `full_but_not_tight(limits, plan, candidates)`: the names of the limits that have room left at
  the plan *and* refuse at least one candidate, sorted by name.

With $`u_{\ell,j}`$ what job $`j`$ uses of limit $`\ell`$, $`C_\ell`$ its cap and $`S`$ the plan,
write first the test for "adding job $`k`$ breaks limit $`\ell`$" and the test for "limit $`\ell`$
has room at the plan", each as an inequality in $`\sum_{j \in S} u_{\ell,j}`$, $`u_{\ell,k}`$ and
$`C_\ell`$. Then code them. Compare amounts with a tolerance of `1e-9`, since uses may be
fractional. The tests use their own district; no solver is needed.
