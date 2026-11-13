A district picks transformer replacements under one budget: maximize $`\sum_j v_j x_j`$ subject to
$`\sum_j c_j x_j \le B`$, $`x_j \in \{0, 1\}`$, with every $`c_j > 0`$. A node LP of the search
returned a point $`x^*`$, and the district wants a plan from it now.

Write `round_and_fill(values, costs, budget, x)` in `fill.py`. Return the sorted list of the items
in the plan built in two steps:

1. **Round down.** Keep item $`j`$ when $`x^*_j \ge 1 - 10^{-6}`$; drop every other item.
2. **Fill.** Go through the items not kept, in order of $`v_j / c_j`$ from highest to lowest (ties
   by item name), and add each one whose cost fits in what is left of the budget. An item that does
   not fit is skipped, and the next one is tried.

The point $`x^*`$ satisfies the budget row, so the rounded-down plan does too.
