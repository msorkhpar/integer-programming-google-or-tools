A bus depot's planners solve a small LP to split weekly overtime hours between engine and brake
work. Their solver interface gives prices but no ranges, and the union is negotiating the
overtime cap. They want to know, for the current cap, how far up or down it can move before its
price changes, found by re-solving.

The row's price, as a function of its right-hand side $`r`$, is constant on intervals and jumps at
**breakpoints**. You are given `build(r)`, which returns a fresh `(model, row)` with the row's
right-hand side set to `r`. Solving that model with GLOP and reading `result.dual_values(row)` gives
the price at `r`; a solve that does not end `OPTIMAL` has no price there.

Write `price_range(build, rhs, low, high, tol=1e-3)` in `ranging.py`. It returns `(lo, hi)`, the
interval around `rhs`, inside `[low, high]`, on which the price equals the price at `rhs` (compare
prices within `1e-9`):

- If the price at `high` is still the same, `hi` is `high` itself (and likewise `lo` is `low`).
- Otherwise there is a change somewhere between `rhs` and `high`: narrow it down by bisection, keeping
  a point with the same price and a point without, until they are within `tol`, and return the
  point with the same price. Do the same toward `low`.
- A right-hand side with no optimal plan does not have the same price.

At a breakpoint itself the solver may report either neighbouring price, so the tests accept any
answer within 0.01 of a breakpoint. About twenty lines.
