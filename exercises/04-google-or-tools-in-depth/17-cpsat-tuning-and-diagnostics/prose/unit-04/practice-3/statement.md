A depot-siting team archives the end of every CP-SAT log. The last block starts with the line
`CpSolverResponse summary:` and holds one `key: value` line per field (`status`, `objective`,
`best_bound`, `branches`, ...), up to the end of the log.

Write two functions in `summary.py`:

- `read_summary(log)`: a dict from each key in that block to its value, both as strings.
- `relative_gap(log)`: the relative gap of the run, as the CP-SAT parameters proto defines it for
  `relative_gap_limit`, with $`O`$ the objective and $`B`$ the best bound:

```math
\text{gap} = \frac{|O - B|}{\max(1, |O|)}
```

The team solves both maximizations and minimizations. About twelve lines.
