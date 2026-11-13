A transmission operator (fictional) assigns one-week line inspections to weeks. Its builder,
`build_slow` in `inspections.py`, is correct and has been reviewed against the formulation, but it
takes minutes on a full year of tasks: every lookup in it scans a whole DataFrame. Your job: make
it at least ten times faster, and prove the models are
identical.

The model, with $`J`$ the tasks, $`S_j`$ the weeks task $`j`$ may use, $`W`$ the weeks of the
capacity table, $`h_j`$ the crew-hours of task $`j`$, $`v_j`$ its value and $`C_w`$ the capacity of
week $`w`$:

```math
\begin{aligned}
& y_{j,w} \in \{0, 1\} && \forall j \in J,\ w \in S_j && \text{(variable } \texttt{y\_}j\texttt{\_}w\text{)} \\
& \max \sum_{j \in J} \sum_{w \in S_j} v_j\, y_{j,w} \\
& \sum_{w \in S_j} y_{j,w} \le 1 && \forall j \in J && (\texttt{once\_}j) \\
& \sum_{j \in J:\ w \in S_j} h_j\, y_{j,w} \le C_w && \forall w \in W && (\texttt{crew\_}w)
\end{aligned}
```

The data is three DataFrames: `tasks` (`task`, `hours`, `value`), `options` (`task`, `week`, one row
per variable) and `capacity` (`week`, `hours`).

Write `build_fast(tasks, options, capacity)` so that `build_fast(...).export_model()` equals
`build_slow(...).export_model()`: the same variables with the same names in the same order, the same
rows in the same order with the same bounds and coefficients, and the same objective. Read
`build_slow` closely for the order it creates things in, and for what it does when a week or a task
has nothing to sum. Any approach that makes the identical model passes: lookups built once
(dictionaries, `groupby`), `mathopt.fast_sum`, or a `ModelProto` built from arrays.

The tests check identity only, never speed, because a speed test would fail on a busy machine.
Run the file to measure the speed-up on 1,500 tasks; the reference is several tens of times faster
than `build_slow` there, and your number will differ. About fifteen lines.
