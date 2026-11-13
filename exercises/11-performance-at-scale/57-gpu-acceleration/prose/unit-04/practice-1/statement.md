A grid operator keeps a record of every LP and MILP run: its `inputs` (a snapshot id), the
`device`, the `solver`, the `method`, the `threads`, the `tolerance`, the `versions`, the `kind`
(`"lp"` or `"milp"`), the `objective` and a `digest` of the solution's bits. When a run is
repeated, the auditors want a verdict that holds a rerun to its bits only where the configuration
promised them, and to a tolerance everywhere else.

Bits are promised when the two runs agree on every one of inputs, device, solver, method, threads,
tolerance and versions, **unless** the method is `"concurrent"` (a race whose winner can change) or
the run is a cuOpt (`solver == "cuopt"`) MILP, whose plans did not repeat with any setting.

Write in `repeats.py`:

- `bits_promised(a, b)`: True when the rule above promises equal bits;
- `verdict(a, b, tol)`: `"not comparable"` when the inputs differ; where bits are promised,
  `"identical"` when digest and objective are equal and `"different"` otherwise; else
  `"within tolerance"` when the objectives differ by at most `tol` relatively (divided by
  $`\max(1, \lvert a\text{'s objective} \rvert)`$), and `"different"` otherwise.

The tests pass run records; no solver runs. About fifteen lines.
