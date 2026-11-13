A road contractor has a pool of identical paving gangs. Each resurfacing job needs a number of
gangs for a number of days, and holds all of them for every day it runs. Days are numbered from 0.

Write `paving_plan(jobs, gangs, horizon)` in `paving.py`. `jobs` maps a job to `(days, gangs it
needs)`, `gangs` is the pool's size, and all work must end by day `horizon`. Return each job's start
day, chosen so that the last job ends as early as possible. If no plan exists, return `{}`.

The model, with $`J`$ the jobs, $`d_j`$ their days, $`g_j`$ the gangs each needs, $`G`$ the pool and
$`H`$ the horizon:

```math
\begin{aligned}
& s_j \in \{0, \dots, H - d_j\} && \forall j \in J && \text{(start day)} \\
& C \in \{0, \dots, H\} \\
& \min \; C \\
& \textstyle\sum_{j \in J \,:\, s_j \le t < s_j + d_j} g_j \le G && \forall t && \text{(gangs)} \\
& C = \max_{j \in J} (s_j + d_j) && && \text{(makespan)}
\end{aligned}
```

The (gangs) rows are one cumulative constraint. Before you read a start back, check the solve's
status. The tests check the plan you return and how early it ends, so any optimal plan passes.
About fifteen lines.
