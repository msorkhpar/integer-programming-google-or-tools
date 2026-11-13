A machine workshop has a pool of mechanics. Each repair needs some mechanics for some days, has a
due day, and costs a penalty for every day it finishes after its due day (a customer's machine
standing idle). Finishing early earns nothing. Days are numbered from 0, and a job that starts on
day `s` and takes `d` days finishes at `s + d`.

Write `least_penalty(jobs, mechanics, horizon)` in `workshop.py`. `jobs` maps a repair to
`(days, mechanics_needed, due, penalty_per_day)`. Return `(total, start)`: the smallest total
penalty, and each job's start day in a plan that achieves it. All work must end by day `horizon`.
Every instance in the tests has a plan.

The model, with $`J`$ the jobs, $`d_j`$, $`m_j`$, $`\delta_j`$ and $`p_j`$ their days, mechanics,
due day and daily penalty, $`M`$ the mechanics and $`H`$ the horizon:

```math
\begin{aligned}
& s_j \in \{0, \dots, H - d_j\},\quad L_j \in \{0, \dots, H\} && \forall j \in J && \text{(start, days late)} \\
& \min \; \textstyle\sum_{j \in J} p_j\, L_j \\
& \textstyle\sum_{j \,:\, s_j \le t < s_j + d_j} m_j \le M && \forall t && \text{(mechanics)} \\
& L_j = \max\big(0,\ s_j + d_j - \delta_j\big) && \forall j \in J && \text{(late}_j)
\end{aligned}
```

The (mechanics) rows are one cumulative constraint; each (late) row is one `add_max_equality`. The
tests check the plan you return and the total, so any optimal plan passes. About twenty lines.
