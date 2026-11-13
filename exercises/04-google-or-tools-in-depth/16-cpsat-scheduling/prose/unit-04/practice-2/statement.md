A museum plans the installation of its new exhibitions. Each job needs some installers for some
days; some jobs, the noisy or dusty ones, must happen while their gallery is closed to visitors.
The museum has a fixed team of installers. Days are numbered from 0, and a job that starts on day
`s` and takes `d` days occupies days `s` to `s + d - 1` and ends at `s + d`.

Write `broken_rules(jobs, start, installers, horizon)` in `checker.py`, **without a solver**: it
checks a plan someone else made. `jobs` maps a job to `(days, installers_needed, windows)`, where
`windows` is a list of closures `(a, b)`, each the half-open span of days $`[a, b)`$ (open from the
start of day `a` to the start of day `b`), or `None` when the job can happen any time. `start` maps
each job to its start day. Return the set of broken rules:

- `("outside", job)` when the job starts before day 0 or ends after `horizon`;
- `("window", job)` when the job has windows and lies wholly inside none of them;
- `("crowded", day)` for each day `t` from 0 to `horizon - 1` on which the installers needed by the
  jobs running exceed `installers`.

The rules, with $`s_j`$, $`d_j`$, $`n_j`$ and $`\mathcal{W}_j`$ each job's start, days, installers
and windows, $`N`$ the team and $`H`$ the horizon:

```math
\begin{aligned}
& 0 \le s_j \;\text{ and }\; s_j + d_j \le H && \forall j && \text{(outside)} \\
& \exists\, [a, b) \in \mathcal{W}_j : a \le s_j \;\text{ and }\; s_j + d_j \le b && \forall j \text{ with windows} && \text{(window)} \\
& \textstyle\sum_{j \,:\, s_j \le t < s_j + d_j} n_j \le N && \forall t \in \{0, \dots, H - 1\} && \text{(crowded)}
\end{aligned}
```

Write each rule the plain way, one loop per rule. The tests hand you plans that break known rules.
About fifteen lines.
