A county roads department buys road-base gravel from several pits. Each pit has a price per ton, a
*fines* content (the share of very small particles, in % of weight) and the tons it can supply. The
specification says the delivered gravel's average fines content must lie between `low` and `high`
percent: too few fines and the base will not compact, too many and it drains badly.

With $`J`$ the pits, $`p_j`$ the price per ton, $`q_j`$ the fines content (%), $`u_j`$ the tons pit
$`j`$ has, $`T`$ the tons needed and $`[\ell, h]`$ the window, the average rule
$`\ell \le \sum_j q_j t_j / \sum_j t_j \le h`$ is multiplied out by the total tons:

```math
\begin{aligned}
\min \;& \sum_{j \in J} p_j\, t_j \\
\text{s.t. }& \sum_{j \in J} t_j = T && && \text{(tons)} \\
& \sum_{j \in J} (q_j - h)\, t_j \le 0 && && \text{(fines\_max)} \\
& \sum_{j \in J} (q_j - \ell)\, t_j \ge 0 && && \text{(fines\_min)} \\
& 0 \le t_j \le u_j && \forall j \in J
\end{aligned}
```

$`t_j`$ is continuous: the tons bought from pit $`j`$. Write `mix(pits, tons, low, high)` in
`blend.py`. It solves this model with GLOP and returns `(status, cost, tons_by_pit)`: the name of
the termination reason; when it is `OPTIMAL`, the cost and a dict from pit name to tons (not
rounded, every pit included); otherwise `None, None`.

About fifteen lines.
