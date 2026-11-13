A water utility's capital model is checked by fixing a planned budget and asking the solver whether
it is allowed, as lesson 10.1.1 did. Before trusting the check, the team wants to know how large an
overspend it can let through, in dollars, for a given row unit and solver.

Write `allowed_overrun(row_size, unit, tol, relative)`. `row_size` is the size of the row's
right-hand side in dollars, `unit` is how many dollars one unit of the row is (1,000 for $k,
1,000,000 for $M), and `tol` is the solver's feasibility tolerance. Return the largest overspend,
in dollars, that the check accepts:

- an **absolute** check (`relative=False`) accepts an overspend of up to `tol` in the row's own
  units, whatever the row's size;
- a **relative** check (`relative=True`) accepts up to `tol` times the larger of 1 and the row's
  size, both measured in the row's own units.

The size of a row is a magnitude: a right-hand side of $-5,000,000 has size $5,000,000.

The tests use their own rows. About four lines.
