A railway closes a line to trains only during **possessions**, agreed stretches of days, and track
work on that line must lie wholly inside one possession. A line also takes one work gang at a time;
gangs on different lines work independently. Days are numbered from 0.

Write `possession_plan(jobs, possessions)` in `possessions.py`. `jobs` maps a job to `(line, days)`;
`possessions` maps a line to its possessions, each `(first_day, last_day)` with both days included.
Return each job's start day, chosen so that the last job ends as early as possible. Every instance in
the tests has a plan.

The model, with $`J`$ the jobs, $`\ell(j)`$ and $`d_j`$ each job's line and days, $`P_\ell`$ the
possessions of line $`\ell`$, and $`L`$ the lines. A job fits in possession $`(f, l)`$ when it starts
on a day from $`f`$ to $`l - d_j + 1`$:

```math
\begin{aligned}
& s_j \in \textstyle\bigcup_{(f, l) \in P_{\ell(j)},\ l - d_j + 1 \ge f} \{f, \dots, l - d_j + 1\} && \forall j \in J && \text{(start inside a possession)} \\
& C \in \{0, \dots, H\},\quad H = \max_{\ell, (f, l) \in P_\ell} (l + 1) \\
& \min \; C \\
& \text{NoOverlap}\big(\{[s_j, s_j + d_j) : \ell(j) = \ell\}\big) && \forall \ell \in L && \text{(line}_\ell) \\
& C = \max_{j \in J} (s_j + d_j) && && \text{(makespan)}
\end{aligned}
```

Build each start's domain with `cp_model.Domain.from_intervals`, whose ranges include both ends.
The tests check the plan you return and how early it ends. About twenty lines.
