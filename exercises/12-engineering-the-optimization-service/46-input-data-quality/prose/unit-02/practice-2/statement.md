A water utility's planning tool exports a main-replacement snapshot each cycle, and this cycle's
export has six defects planted in it. Your gate must reject it, and find all six.

Each job $`j`$ has a cost profile $`c_{j,0}, c_{j,1}, \dots`$ (one entry per year of work, $k), a
window $`e_j \le t \le l_j`$ of start years, a `required` flag, and possibly a prerequisite $`a(j)`$
with a lag $`L_j`$: job $`j`$ may start in year $`t`$ only if $`a(j)`$ started in a year
$`s \le t - L_j`$. Each year $`y`$ of the horizon $`H`$ has a budget $`B_y`$. The model has
$`x_{j,t} \in \{0, 1\}`$ for each start year $`t \in T_j`$, where $`T_j`$ holds the window's years
whose whole work falls inside the horizon: the snapshot's `horizon` is a list of consecutive years,
and $`t`$ is in $`T_j`$ when $`e_j \le t \le l_j`$, $`t`$ is at least the horizon's first year, and
$`t + |c_j| - 1`$ (the job's last year of work) is at most the horizon's last year. The rows are

```math
\begin{aligned}
\sum_{t \in T_j} x_{j,t} &= 1 && \forall j \text{ required} && \text{(required}_j) \\
\sum_{t \in T_j} x_{j,t} &\le 1 && \forall j \text{ optional} && \text{(once}_j) \\
\sum_{u \in T_j,\, u \le t} x_{j,u} &\le \sum_{s \in T_{a(j)},\, s \le t - L_j} x_{a(j),s} && \forall j \text{ with } a(j),\ t \in T_j && \text{(after}_{j,t}) \\
\sum_{j} \sum_{t \in T_j,\, 0 \le y - t < |c_j|} c_{j,\,y-t}\, x_{j,t} &\le B_y && \forall y \in H && \text{(budget}_y)
\end{aligned}
```

In `review.py`, write `starts` (the set $`T_j`$) and the five rules, and `review(snapshot, previous)`,
which returns every finding as `(severity, rule, subject)`, sorted. `rejected` is written.

| rule | subject | fires when | severity |
| --- | --- | --- | --- |
| `prerequisite-cycle` | the jobs on the cycle, sorted, joined with `+` | following prerequisites from a job leads back to it | error |
| `prerequisite-too-late` | the job | no start of its prerequisite plus the lag reaches any of its own starts | error or warning, below |
| `no-start-in-horizon` | the job | a required job has no start year | error |
| `required-over-budget` | `plan` | what every plan must pay for costs more than all budgets together | error |
| `budget-drift` | the year, as text | a year's budget is more than 3 times, or less than a third of, its amount in `previous` | warning |

Give `prerequisite-too-late` the severity the lesson's rule calls for: an error when the finding
proves no plan exists, a warning otherwise. The finding proves it when the job must be done in every
plan: the job is required, or it is the prerequisite (directly or through a chain of `after`) of a
required job. A job that is optional and needed by no required job can simply be left out, so its
finding is a warning. The same set of must-do jobs is what `required-over-budget` adds up. With no
`previous`, there is no drift.

The six planted defects are one of each: a prerequisite cycle, a too-late prerequisite on a job
every plan must do, a too-late prerequisite on an optional job, a required job with no start year,
required spending above all budgets together, and a budget that drifted from `previous`. The main
test checks that `review` finds each of them. About forty lines.
