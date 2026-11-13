A water treatment plant doses two chemicals each day. Its LP's rows are limits on stock, on the
mixer's hours and on a minimum disinfection level. After each solve, the shift lead wants a
report: for every row, how much room it has left and what it is worth.

Write `row_report(model, result, tol=1e-6)` for a solved LP. Return a dict keyed by each row's
name, whose value is a dict with three entries:

- `"slack"`: how far the row's left side sits from its nearest **finite** bound, at the
  solution. A row may have a lower bound, an upper bound, or both (an equality has both, equal);
  a missing bound is infinite.
- `"binding"`: `True` when that slack is zero, within `tol`.
- `"price"`: the row's dual value.

Define binding first, in one sentence, from the row's two sides alone, then write the code. Each
row's left side is a sum of coefficient × variable value: `row.terms()` yields the terms, each
with `.variable` and `.coefficient`, and `row.lower_bound` and `row.upper_bound` are its bounds.
`model.linear_constraints()` yields the rows.

The tests build small LPs, solve them with GLOP and read your report. About ten lines.
