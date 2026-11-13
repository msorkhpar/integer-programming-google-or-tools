A logistics team benchmarks its solvers on a fixed instance set with several seeds, the way lesson
5.4.2 built GridCap's harness. The solving itself is behind one function the team already has:
`solve(solver, instance, seed)` returns `(solved, work)`, whether the run proved optimality and the
solver's deterministic work count. `shifted_geometric_mean(values, shift)` is given in `harness.py`.

Write `benchmark(solve, solvers, instances, seeds, shift, cap)`. For every solver, instance and seed
(a **cell**), call `solve` twice. Return, for each solver, a dict with:

- `"runs"`: the number of cells;
- `"solved"`: how many cells' first run solved;
- `"repeat"`: `True` only if, in every cell, the two runs returned the same `(solved, work)`;
- `"sgm"`: the shifted geometric mean, with `shift`, of the first runs' work, where a run that did
  not solve counts as `cap`.

The tests call it with a stand-in `solve`, so no solver runs. About twelve lines.
