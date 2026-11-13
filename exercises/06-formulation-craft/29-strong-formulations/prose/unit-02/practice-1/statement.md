A regulator (not GridCap) chooses which field inspections to run next quarter. Inspection $`j`$
costs $`c_j`$ and gives $`h_{d,j}`$ hours of inspection to district $`d`$; each district must get at
least $`r_d`$ hours, and the total cost is capped by $`B`$:

```math
\begin{aligned}
\sum_j c_j\, x_j &\le B && && \text{(budget)} \\
\sum_j h_{d,j}\, x_j &\ge r_d && \forall d && \text{(cover}_d) \\
x_j &\in \{0, 1\} && \forall j
\end{aligned}
```

`build` in `inspections.py` writes this model and can apply fixings to the variables' bounds.

Before solving, the planners want the facts the rows force on their own: inspections every allowed
plan includes (fixed at 1) and inspections no allowed plan includes (fixed at 0). Write
`tighten(cost, budget, hours, need)`, returning the pair `(ones, zeros)` of sets.

The lesson fixed starts at 0 from "$`\le`$" rows. Here the coverage rows are "$`\ge`$" rows, so work
out on paper what they can force, and how. Use one row at a time: a coverage row, given what is
already fixed at 0, and the budget row, given what is already fixed at 1. A fixing found from one row
can make another row force something new, so repeat until a whole pass finds nothing. Write the
condition for each kind of fixing as an inequality before coding it.

The tests compare your sets with the ones this one-row-at-a-time rule reaches, and check every fixing
against all allowed plans, found by brute force. About fifteen lines.
