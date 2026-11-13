An engineering team approximates smooth curves (pump efficiency, failure cost, value of a renewal)
by piecewise-linear ones before they go into a MILP. They want a rule instead of a habit: use the
**fewest equally spaced breakpoints** whose curve stays within a tolerance of the true one.

Write `fewest_breakpoints(f, lo, hi, tol, max_n=65)`:

- `f` is the true function on `[lo, hi]`. A curve with `n` breakpoints (`n >= 2`) puts them at
  `lo + (hi - lo) * k / (n - 1)` for `k = 0, ..., n - 1`, with the true values there, and joins
  neighbours by straight lines.
- Its **gap** is the largest `|f(x) - curve(x)|` over the 1,001 evenly spaced points
  `lo + (hi - lo) * i / 1000`, `i = 0, ..., 1000`.
- Return the smallest `n` from 2 to `max_n` whose gap is at most `tol`, or `None` if none is.

The tests use curves of different shapes, so make no assumption about where on a segment the gap is
largest. About fifteen lines.
