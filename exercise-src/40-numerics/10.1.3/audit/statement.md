A freight company runs its depot-opening model with HiGHS some nights and SCIP others. HiGHS's
report prints the largest bound, integrality and row violation of the plan it returns; SCIP's
does not. The team wants the same three numbers for every plan, whichever solver produced it.

Write `audit(model, values)` for a MathOpt model and a solution's values (a dict from each
variable to its value, as `result.variable_values()` returns it). It returns a dict with three
keys, each the largest violation of its kind, or 0.0 when there is none:

- `"bound"`: how far a variable's value is outside its bounds, below the lower or above the upper;
- `"integrality"`: for integer variables only, how far the value is from the nearest whole number;
- `"row"`: how far a row's activity (the sum of its coefficients times the values) is outside its
  bounds, below the lower side or above the upper.

`model.variables()` and `model.linear_constraints()` yield the variables and rows; a variable has
`lower_bound`, `upper_bound` and `integer`; a row has `lower_bound` and `upper_bound`, and
`model.row_nonzeros(row)` with `row.get_coefficient(variable)` gives its terms. Infinite bounds
never count as broken. The tests build their own models and values, with no solve. About twelve
lines.
