A team benchmarking LP methods wants one helper that runs a model with a named solver and a named
LP algorithm and reports how much work the algorithm did, so a table of methods can be built from
its results without anyone reading logs.

Write `run_method(model, solver, algorithm)` in `methods.py`. It solves `model` with
`mathopt.solve(model, solver, params=mathopt.SolveParameters(lp_algorithm=algorithm))` and returns
a tuple `(status, iterations)`:

- `status` is the termination reason's name (`"OPTIMAL"`, ...);
- `iterations` is the count that matches the algorithm's kind, read from `result.solve_stats`:
  `simplex_iterations` for `PRIMAL_SIMPLEX` and `DUAL_SIMPLEX`, `barrier_iterations` for
  `BARRIER`, `first_order_iterations` for `FIRST_ORDER`.

A solver that does not offer the algorithm raises an exception from `mathopt.solve`. Then the
function returns `("REFUSED", 0)`. It never falls back to the solver's default algorithm, because
a benchmark row labelled "barrier" that was solved by simplex is a wrong row. Catch the exception
around the solve call only; in OR-Tools 9.15 the exception's type is an accident of the wrapper,
so catch `Exception`.

The model the tests pass in is their own; the function never builds one.
