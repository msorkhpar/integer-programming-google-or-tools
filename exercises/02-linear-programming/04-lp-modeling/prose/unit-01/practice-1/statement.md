A city transit agency splits its maintenance budget across its modes: bus, rail and ferry. The
council has passed two kinds of rule, both written as ratios:

- no mode gets more than a share `max_share` of the total spent;
- for each pair `(a, b, ratio)` in `pairs`, mode `a` gets at least `ratio` times what mode `b` gets
  (the council wrote it as "a / b must be at least ratio").

With $`K`$ the modes, $`x_k \ge 0`$ the amount spent on mode $`k`$, $`\alpha`$ the largest share and
$`P`$ the pairs, the rules are:

```math
\begin{aligned}
\frac{x_k}{\sum_{j \in K} x_j} &\le \alpha && \forall k \in K && \text{(share}_k) \\
\frac{x_a}{x_b} &\ge \rho && \forall (a, b, \rho) \in P && \text{(ratio}_{a,b})
\end{aligned}
```

Neither is linear as written. Multiply each one out first (every amount is $`\ge 0`$), then write
`add_share_rules(model, spend, max_share, pairs)` in `rules.py`: it adds one row per mode and one
row per pair to `model`, where `spend` maps each mode to its variable. Name the rows `share_<mode>`
and `ratio_<a>_<b>`.

The tests fix every amount to a plan's value and ask GLOP whether your rows allow it, so any correct
linear form passes. About five lines.
