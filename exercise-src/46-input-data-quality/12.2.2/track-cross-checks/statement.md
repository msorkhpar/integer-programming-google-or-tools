A rail operator plans track and signal renewals over a few years. Each job uses one crew type for
a number of crew-weeks; each crew type has a supply of crew-weeks over the whole horizon. Some jobs
are required, a job may need another job done first (`after`), and some jobs are alternatives:
at most one job of each `exclusive` group may be done. The operator's model, with $`J`$ the jobs,
$`R \subseteq J`$ the required jobs, $`a(j)`$ the prerequisite of job $`j`$ (if any), $`E_g`$ the
jobs of exclusive group $`g`$, $`w_j`$ the crew-weeks of job $`j`$, $`k(j)`$ its crew type and
$`S_k`$ the supply of crew type $`k`$:

```math
\begin{aligned}
z_j &\in \{0, 1\} && \forall j \in J && \text{(job } j \text{ is done)} \\
z_j &= 1 && \forall j \in R && \text{(required}_j) \\
z_j &\le z_{a(j)} && \forall j \text{ with a prerequisite} && \text{(after}_j) \\
\sum_{j \in E_g} z_j &\le 1 && \forall g && \text{(exclusive}_g) \\
\sum_{j:\, k(j) = k} w_j\, z_j &\le S_k && \forall k && \text{(crew}_k)
\end{aligned}
```

The snapshot has passed its schema. Before the solve, find the clashes between jobs that prove no
plan exists. First write down which jobs every plan must do, and why the rows force each of them.
Then, in `cross.py`, write `required(snapshot)` and `cross_checks(snapshot)`, which returns a sorted
list of `(rule, subject)` pairs:

- `("exclusive-required", g)`, once per exclusive group $`g`$ that holds two or more jobs every plan
  must do;
- `("crew-short", k)` for each crew type $`k`$ whose supply is below the crew-weeks of the jobs
  every plan must do.

A rule may fire only when no plan can exist. The schema has already checked that every job's crew
type is a key of `crews`, so you may assume it; the reference loops over the crew types in `crews`
and would never report a type missing from it. About fifteen lines.
