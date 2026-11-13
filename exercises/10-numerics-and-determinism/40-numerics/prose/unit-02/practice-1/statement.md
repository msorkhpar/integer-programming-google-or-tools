A hospital network's staffing model prints `Matrix [1e-04, 1e+08]` at the top of its HiGHS log.
The span is far too wide, but the log does not say which rows and variables hold the extremes, and
the model has thousands of rows. The team wants a function that names them.

Write `matrix_extremes(model)` for a MathOpt model. It returns two triples, the smallest and the
largest matrix entry by absolute value, each as `(row name, variable name, coefficient)`, with the
coefficient as written in the row, sign included. Only the rows' coefficients count: the
objective's coefficients and the variables' bounds are other ranges. Every row in the tests has at
least one nonzero coefficient.

`model.linear_constraints()` yields the rows, `model.row_nonzeros(row)` yields the variables with a
nonzero coefficient in a row, and `row.get_coefficient(variable)` reads one coefficient. About five
lines.
