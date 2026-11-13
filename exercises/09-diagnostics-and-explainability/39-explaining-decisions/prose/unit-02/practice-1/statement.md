A regional library board picks branch renovations each year with a small MILP: each renovation has
a cost and a benefit, the year's budget is fixed, and renovations required by accessibility law are
mandatory. Branch managers keep asking the same two questions: "why was my renovation left out?"
and "why did theirs get in?". The board wants one answer to both: what the best plan would lose if
that one decision went the other way, and which renovations would change.

`renovations.py` already has the board's model (`build`) and `best`, which solves a model and
returns the best value and the chosen names, or `None` when no plan is feasible. `best` solves at a
relative gap of 0, so both values in a cost are proven optima, as the lesson requires. Write
`forcing_cost(items, budget, name)`. It returns a dictionary:

- `"action"`: `"out"` if the best plan chose `name`, `"in"` if it did not;
- `"cost"`: the best plan's value less the best value with that decision reversed, rounded to an
  integer, or `None` when no plan allows the reversal;
- `"dropped"` and `"added"`: the names in the best plan but not in the reversed one, and the other
  way round, each sorted; both empty when there is no reversed plan.

The board's model, with $`R`$ the renovations, $`M \subseteq R`$ the mandatory ones, $`c_r`$ and
$`v_r`$ each renovation's cost and value, and $`B`$ the budget:

```math
\begin{aligned}
\max \;& \sum_{r \in R} v_r\, x_r \\
\text{s.t. }& \sum_{r \in R} c_r\, x_r \le B && \text{(budget)} \\
& x_r = 1 && \forall r \in M && \text{(must}_r) \\
& x_r \in \{0, 1\} && \forall r \in R
\end{aligned}
```

Write the one row your reversal adds, with its label, for each of the two actions. Then code it:
add it as a named row to a fresh copy of the model. The tests use their own branches.
