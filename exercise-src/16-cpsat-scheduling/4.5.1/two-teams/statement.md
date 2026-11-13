A water utility has inspection teams that can each do any job, one job at a time. Some teams are
away on some days, given as `(first_day, last_day)` pairs, both days included. Days are numbered
from 0.

Write `split_work(jobs, teams, away, horizon)` in `teams.py`. `jobs` maps a job to its days of work,
`teams` lists the team names, `away` maps a team to its absences (a team with none may be missing
from it), and all work must end by day `horizon`. Return, for each job, the pair
`(team, start_day)`, chosen so that the last job ends as early as possible.

The model, with $`J`$ the jobs, $`d_j`$ their days, $`T`$ the teams, $`A_t`$ team $`t`$'s
absences with first and last days $`f_a`$ and $`l_a`$, and $`H`$ the horizon:

```math
\begin{aligned}
& s_j \in \{0, \dots, H - d_j\} && \forall j \in J && \text{(start day)} \\
& x_{j,t} \in \{0, 1\} && \forall j \in J,\ t \in T && \text{(team } t \text{ does job } j\text{)} \\
& C \in \{0, \dots, H\} \\
& \min \; C \\
& \textstyle\sum_{t \in T} x_{j,t} = 1 && \forall j \in J && \text{(one\_team}_j) \\
& \text{NoOverlap}\big(\{[s_j, s_j + d_j) \text{ present iff } x_{j,t} = 1 : j \in J\} \cup \{[f_a, l_a + 1) : a \in A_t\}\big) && \forall t \in T && \text{(team}_t) \\
& C = \max_{j \in J} (s_j + d_j) && && \text{(makespan)}
\end{aligned}
```

The interval "present iff $`x_{j,t} = 1`$" is an optional interval with presence literal
$`x_{j,t}`$; job $`j`$ has one per team, all on the same $`s_j`$. The tests check the plan you
return and how early it ends, so any optimal plan passes. About twenty lines.
