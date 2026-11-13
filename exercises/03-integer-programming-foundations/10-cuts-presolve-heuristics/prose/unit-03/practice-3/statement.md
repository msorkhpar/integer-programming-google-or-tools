A feeder-reinforcement model maximizes $`\sum_j v_j x_j`$ subject to $`\sum_j c_j x_j \le B`$ and
$`x_j \in \{0, 1\}`$. The search has an incumbent plan $`\hat x`$ and an LP optimum $`x^*`$. Write
the RINS step for it.

Write `rins(values, costs, budget, incumbent, x)` in `rins.py`. `incumbent` maps each item to 0 or 1
and `x` maps it to its LP value.

1. **Fix where they agree.** Item $`j`$ is fixed at $`\hat x_j`$ when
   $`|x^*_j - \hat x_j| < 10^{-6}`$; every other item is free.
2. **Solve the neighbourhood.** Over every 0-1 choice of the free items, with the fixed items at
   their values, keep the choices whose total cost (fixed items included) is at most $`B`$, and
   return the sorted list of the items in the most valuable one. On a tie, keep the one found first
   when the free items, sorted by name, are tried with `itertools.product((0, 1), repeat=...)`.

If no choice fits the budget (it happens only when the items fixed at 1 already cost more than
$`B`$, so the incumbent itself broke the budget), there is no plan in the neighbourhood: return
`None`, not an empty list, since the empty plan is not in the neighbourhood either. The reference
solution does exactly that.

The tests have at most four free items, so trying every choice is fast.
