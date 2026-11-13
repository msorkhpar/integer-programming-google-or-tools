An analytics team has timed its LP solvers on its own machine: several CPU and GPU solvers, several
LP sizes $`n`$, each run repeated. Each record holds the `solver`, the `device` (`"cpu"` or
`"gpu"`), the size `n`, the `seconds`, whether it was the process's first GPU solve
(`first_in_process`), and its `rel_error` against a CPU reference. They want two numbers per
decision, computed by a rule, not by eye:

- `speedups(records, needed)`: for each size, the **speed-up** = (best CPU solver's time) / (best GPU
  solver's time), where a solver's time is the **median** of its runs at that size, a process's first
  GPU solve is left out (it also starts CUDA), and a GPU solver counts only if every run of it at that
  size has `rel_error <= needed`. A run left out as a process's first is left out of that accuracy
  check too: an inaccurate first run does not disqualify its solver. The value is None when no GPU
  solver counts, and None when the size has no CPU run (there is nothing to compare with). Return a
  dict from every size in the records to its speed-up.
- `crossover(table)`: the smallest size from which the GPU is faster (speed-up above 1) at that size
  **and at every larger size** in the table, or None.

Write both in `speedup.py`. The tests pass lists of records; no solver runs. About twenty lines.
