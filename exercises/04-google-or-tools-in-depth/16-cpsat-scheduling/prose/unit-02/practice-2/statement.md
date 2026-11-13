The paving contractor's pool shrinks over the holidays: `available[t]` is the number of gangs on
day `t`, for every day of the horizon. Each job needs `(days, gangs)` as before and holds its gangs
for every day it runs. Days are numbered from 0.

Write `holiday_plan(jobs, available)` in `gang_days.py`. The horizon is `len(available)`. Return each
job's start day, chosen so that the last job ends as early as possible. Every instance in the tests
has a plan.

The model, with $`J`$ the jobs, $`d_j`$ and $`g_j`$ their days and gangs, $`a_t`$ the gangs on day
$`t`$, $`H`$ the horizon and $`G = \max_t a_t`$:

```math
\begin{aligned}
& s_j \in \{0, \dots, H - d_j\} && \forall j \in J && \text{(start day)} \\
& C \in \{0, \dots, H\} \\
& \min \; C \\
& \textstyle\sum_{j \in J \,:\, s_j \le t < s_j + d_j} g_j \;+\; (G - a_t) \;\le\; G && \forall t && \text{(gangs)} \\
& C = \max_{j \in J} (s_j + d_j) && && \text{(makespan)}
\end{aligned}
```

The (gangs) rows are one cumulative constraint of capacity $`G`$ in which the $`G - a_t`$ missing
gangs are held by fixed intervals. Group consecutive days with the same $`a_t`$ into one fixed
interval each (a run of days is one interval, as long as the run), and add none where
$`a_t = G`$. The tests check the plan you return and how early it ends. About twenty lines.
