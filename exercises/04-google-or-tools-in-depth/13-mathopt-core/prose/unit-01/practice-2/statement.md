A transit agency's planners review every new model in a pull request, and they want its rows as
text they can read against the formulation. You have the model; MathOpt stores each row as
$`\text{lb} \le \sum_j a_j x_j \le \text{ub}`$, with an infinite bound on a one-sided row.

Write `describe(row)` in `rows.py`: one line for one `mathopt.LinearConstraint`, in this form.

- It starts with the row's name and a colon: `budget: `.
- The terms come next, sorted by variable name. Each is the coefficient, a space and the variable's
  name (`3 x_bus`), with the coefficient written by Python's `:g` format (`2.5`, `10`, `0.001`). A
  coefficient of 1 is left out (`x_bus`). After the first term, each term is joined with ` + ` or, when
  its coefficient is negative, with ` - ` and the coefficient's absolute value (`3 x_a - 2 x_b`). A
  first term that is negative starts with a minus sign and no space (`-2 x_b`, or `-x_b` for $`-1`$).
- Then the bounds: `terms <= ub` when only the upper bound is finite, `terms >= lb` when only the lower
  bound is, `terms == lb` when the two bounds are equal, and `lb <= terms <= ub` when both are finite
  and different, each number written with `:g`.

For example, $`3 x_a + 2 x_b \le 10`$ named `budget` reads `budget: 3 x_a + 2 x_b <= 10`.

Then write `describe_model(model)`: the list of `describe(row)` for every row of the model, in the
order the rows were created. Read the row through its handle: its `name`, `lower_bound`,
`upper_bound` and `terms()`, each term with a `variable` and a `coefficient`.
