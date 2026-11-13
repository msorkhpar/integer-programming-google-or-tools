The port authority's real list has 60 candidate repairs, so checking all $`2^{60}`$ subsets is out
of the question. It still wants to know how many subsets fit the budget, as a lower bound on its
open plans when only the budget touches those repairs.

Write `count_within(costs, budget)` in `within.py`: the number of subsets of the projects (the
empty one included) whose total cost is at most `budget`. Costs and the budget are whole numbers,
costs are positive.

Use a table, not a list of subsets. Let `ways[b]` be the number of subsets of the projects seen so
far that cost exactly `b`, for every `b` from 0 to the budget. Before any project, `ways[0] = 1`
(the empty subset) and every other entry is 0. A project of cost `c` updates the table with

```math
\text{ways}[b] \mathrel{+}= \text{ways}[b - c] \qquad \text{for } b \text{ from the budget down to } c
```

The answer is the sum of the final table. Work out why the loop must run downward before you write
it. About six lines.
