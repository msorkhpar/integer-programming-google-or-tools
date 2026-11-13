A school district's facilities office solves an LP each spring to split its repair money. Every
year some kinds of work get nothing, and their sponsors ask the same question: "how much better
would our work have to be to get funded?" The office wants the answer for every unfunded kind of
work, from one solve.

For an LP solved to optimality, a variable $`x_j`$ that the plan leaves at 0 has reduced cost
$`d_j`$ (MathOpt's `result.reduced_costs(var)`). Its **entry value**, the objective coefficient at
which it starts to pay, is

```math
c_j - d_j
```

where $`c_j`$ is its coefficient in the objective (`model.objective.get_linear_coefficient(var)`).
The formula holds for a maximization ($`d_j \le 0`$, so the entry value is above $`c_j`$) and for a
minimization ($`d_j \ge 0`$, so it is below).

Write `entry_values(model, tol=1e-9)` in `entry.py`. Solve `model` with GLOP. If the solve does not
end `OPTIMAL`, return `{}`. Otherwise return a dict mapping the name of every variable whose value
is within `tol` of 0 to its entry value; variables in use do not appear.

About ten lines.
