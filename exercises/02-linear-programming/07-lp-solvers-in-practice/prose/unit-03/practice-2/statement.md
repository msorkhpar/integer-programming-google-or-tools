A maintenance contractor sells crew hours to three clients and plans them with a small LP. Before
a budget meeting its finance lead wants two numbers for each proposed cut: what the dual value of
the budget row predicts, and what a re-solve says. Where they differ, the meeting needs the
re-solve. The LP is given as `build()` in the starter, with $`h_A, h_B, h_C`$ the hours sold:

```math
\begin{aligned}
\max \;& 6 h_A + 5 h_B + 2 h_C \\
\text{s.t. }& 2 h_A + 2 h_B + h_C \le 20 && \text{(budget)} \\
& 0 \le h_A \le 4, \quad 0 \le h_B \le 5, \quad 0 \le h_C \le 10
\end{aligned}
```

Write `what_if(model, row, cut)` in `what_if.py`. It returns a tuple `(predicted, actual)`:

- solve the model as given with GLOP; read the objective $`z`$ and the row's dual value
  $`y`$ with `result.dual_values(row)`;
- `predicted` is $`z - y \cdot \text{cut}`$: the objective the dual value predicts after the
  row's upper bound drops by `cut`;
- lower the row's `upper_bound` by `cut`, solve again, and `actual` is that solve's objective;
- put the row's upper bound back before returning, so the model is left as it was given.

Every cut the tests ask about leaves the model feasible.
