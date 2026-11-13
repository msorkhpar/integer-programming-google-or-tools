A hospital's supply team keeps a purchasing model in MathOpt: order quantities, storage limits,
supplier rebates and credits, some of them continuous with no upper bound. After a refactor the
model came back `UNBOUNDED` in production, and the team wants a check that runs *before* the
solve and names the variables that could be to blame.

A variable can make a feasible model unbounded on its own when three things hold together:

1. the objective rewards moving it one way (up for a positive coefficient in a maximization, down
   for a negative one; the reverse in a minimization);
2. it has no bound on that side (`upper_bound` or `lower_bound` is infinite);
3. no row stops it going that way. A row $`\ell \le \sum_j a_j x_j \le u`$ stops $`x_j`$ from
   growing when $`a_j > 0`$ and $`u`$ is finite, or $`a_j < 0`$ and $`\ell`$ is finite; it stops
   $`x_j`$ from falling in the two mirror cases.

Write `free_to_grow(model)` returning the sorted names of every variable for which all three hold.
Useful calls: `model.objective.is_maximize`, `model.objective.get_linear_coefficient(v)`,
`model.variables()`, `model.linear_constraints()`, and for a row `row.terms()` (each term has
`.variable` and `.coefficient`) and `row.lower_bound`, `row.upper_bound` (infinite when absent).

This check is a cheap first look: a variable it names makes any feasible model unbounded, but a
model can be unbounded along a direction that moves several variables at once, which it does not
see. The tests build small models and compare the names. About twenty lines.
