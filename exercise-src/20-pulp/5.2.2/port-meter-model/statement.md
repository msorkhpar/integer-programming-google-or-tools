A water utility plans its smart-meter rollout with an inherited PuLP model, `legacy_build` in
`meters.py`. Its planning service is moving to MathOpt, and the team lead will accept the port only
with proof that it gives the legacy model's answers.

Write `port_build(sites, budget, crew_weeks)` in `meters.py`: the legacy model in MathOpt, with the
same variable names and the same row names. It returns the model, the site variables `x[sid]` and
the extra-crews variable. `port_solve`, already written, solves it with SCIP at a gap of 0 and
reads the answer. Leave `legacy_build` as it is.

The legacy model, read off the PuLP code. $`S`$ is the sites, $`D`$ the districts and $`S_d`$ the
sites of district $`d`$. Site $`i`$ brings a benefit $`b_i`$ ($k a year), costs $`c_i`$ ($k) and
takes $`w_i`$ installer crew-weeks. The year has a budget $`B`$ and $`W`$ crew-weeks, and each
extra crew hired costs $40k and adds 10 crew-weeks.

```math
\begin{aligned}
\max\ & \sum_{i \in S} b_i\, x_i - 40\, k && && \text{(net)} \\
& \sum_{i \in S} c_i\, x_i \le B && && \text{(budget)} \\
& \sum_{i \in S} w_i\, x_i \le W + 10\, k && && \text{(crew)} \\
& \sum_{i \in S_d} x_i \ge 1 && \forall d \in D && \text{(cover}_d) \\
& x_i \in \{0, 1\} \ \ \forall i \in S, \qquad k \in \{0, 1, 2, 3\}
\end{aligned}
```

Check your variables against the PuLP code, not only against this page: a bound or a type that
the PuLP call states is easy to drop in a port. The solve uses SCIP rather than HiGHS because the
tests import PuLP in the same process. About eight lines.
