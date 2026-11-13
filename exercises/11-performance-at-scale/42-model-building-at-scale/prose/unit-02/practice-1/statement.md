A transmission operator (fictional) schedules line inspections week by week. Each task may start
in some weeks, and needs a given number of crew-hours in each week of its work: a three-week
inspection might need 5, 0 and 3 hours (the middle week waits for a permit). Each week has a crew
capacity. The planners' data arrives as two DataFrames, and you are to build the capacity rows'
coefficients as one table, the way lesson 11.1.2 builds the budget rows.

The model's capacity rows, with $`J`$ the tasks, $`S_j`$ the weeks task $`j`$ may start in, $`W`$
the planning weeks, $`h_{j,k}`$ the crew-hours task $`j`$ needs in its $`k`$-th week of work
($`k = 0`$ is its start week) and $`C_w`$ the capacity of week $`w`$:

```math
\begin{aligned}
& y_{j,s} \in \{0, 1\} && \forall j \in J,\ s \in S_j && \text{(task } j \text{ starts in week } s\text{)} \\
& \sum_{j \in J} \sum_{s \in S_j,\ s \le w} h_{j,\,w-s}\; y_{j,s} \le C_w && \forall w \in W && \text{(crew}_w\text{)}
\end{aligned}
```

Write `hours_entries(options, profile, weeks)` in `entries.py`. `options` has one row per variable
$`y_{j,s}`$, with columns `task` and `start`; the variable's column number is its position in
`options`: 0 for the first row, 1 for the next, and so on. `profile` has columns `task`, `k` and
`hours`. `weeks` lists the planning weeks.

Return a DataFrame with columns `week`, `col` and `coef`, one row per nonzero coefficient of the
$`\text{crew}_w`$ rows: the variable in column `col` carries `coef` hours in week `week`'s row. Leave
out zero coefficients and weeks outside `weeks`, and sort the rows by week, then by column (the
row-major order a `ModelProto` wants). Use joins and filters on whole columns; no loop over rows is
needed. About eight lines.
