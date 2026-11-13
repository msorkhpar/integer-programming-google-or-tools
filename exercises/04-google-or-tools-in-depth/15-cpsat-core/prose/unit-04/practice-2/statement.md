A drainage contractor (not GridCap) has one crew and a list of culvert repairs. The crew does one
repair at a time, with no gaps needed. Each job $`j`$ takes $`d_j`$ days, is due on day $`u_j`$, and
each day it finishes late costs $`w_j`$. Find the order with the least weighted lateness.

Write `best_order(jobs)` in `crews.py`. It returns `(cost, order)`: the least total weighted lateness
as an `int`, and the job names in the order the crew does them. Use CP-SAT and the formulation of the
lesson's crew order, with $`H = \sum_j d_j`$:

```math
\begin{aligned}
\min \;& \sum_{j \in J} w_j\, \ell_j \\
\text{s.t. }& \ell_j \ge s_j + d_j - u_j && \forall j \in J && \text{(late}_j) \\
& y_{jk} \Rightarrow s_j + d_j \le s_k && \forall j < k && \text{(before}_{jk}) \\
& \lnot y_{jk} \Rightarrow s_k + d_k \le s_j && \forall j < k && \text{(after}_{jk}) \\
& s_j \in \{0, \dots, H\},\ \ell_j \in \{0, \dots, H\},\ y_{jk} \in \{0, 1\}
\end{aligned}
```

Read the order off the start days. The tests compare your answer with every possible order. About
fifteen lines.
