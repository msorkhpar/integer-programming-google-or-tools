A pipeline firm hires inspection crews by the season. Each job is a whole number of crew-months
that one crew must do whole, and a season holds `season` crew-months. How few seasons (crews) cover
every job?

Write `fewest_crews(sizes, season)` in `packing.py`, as a MathOpt model. Return the number of
seasons used and the jobs in each used season, as `(count, [[job indices], ...])`, or `None` when
no packing exists.

The model, with $`B`$ the seasons offered, $`x_{i,b} = 1`$ when job $`i`$ goes in season $`b`$ and
$`y_b = 1`$ when season $`b`$ is used:

```math
\begin{aligned}
\min\;& \sum_{b \in B} y_b \\
\text{s.t. }& \sum_{b \in B} x_{i,b} = 1 && \forall i && \text{(once}_i) \\
& \sum_i s_i\, x_{i,b} \le S\, y_b && \forall b \in B && \text{(cap}_b) \\
& x_{i,b},\ y_b \in \{0, 1\}
\end{aligned}
```

Offer enough seasons that a packing always exists when every job fits in one season: one season
per job, `len(sizes)` seasons in all, as the reference offers, is always enough (each job alone in its own
season). Read the answer only when the solve is optimal, and return `None` otherwise (a job longer
than the season makes the model infeasible). Return the count as an `int`, with
`round(result.objective_value())`, and leave out the empty seasons from the list. Solve with
`mathopt.SolverType.CP_SAT`. About fifteen lines.
