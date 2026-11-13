A regulator requires each maintenance district to spend at least a floor $`F`$ ($k) this year,
**unless** the district is granted a waiver. The district's spend is the sum of its work orders.
Each work order $`j`$ has a continuous spend $`s_j`$ between a lowest and a highest amount (some
orders are already committed, so their lowest amount is above 0, and a credit line, money returned
to the district, has a negative lowest amount). The waiver is a binary $`w`$.

Write `add_floor(model, spend, floor, waiver)` in `floor.py`. `spend` maps each work order's name to
its MathOpt variable, whose bounds (`lower_bound`, `upper_bound`) are the order's lowest and highest
spend. Write the rule as one big-M row, and compute its $`M`$ from those bounds: the smallest value
that never refuses a plan the bounds allow when the waiver is on. The lesson derived $`M`$ for a
"$`\le`$ unless" row; this one is a floor, "$`\ge`$ unless".

The model so far, with $`O`$ the work orders and $`l_j \le s_j \le u_j`$ their bounds:

```math
\begin{aligned}
& l_j \le s_j \le u_j && \forall j \in O \\
& w \in \{0, 1\} && \\
& \text{?} && \text{(district\_floor)}
\end{aligned}
```

Write the row in this notation first, with the formula for $`M`$, then code it. Check it by hand on
a district whose orders are all at their lowest spend, with and without the waiver.

The tests fix a plan by its variables' bounds, after your row is written, and ask the solver whether
the plan is allowed, so any correct row passes. One more test relaxes the waiver to one half and
checks that your $`M`$ is as small as the bounds allow. About three lines.
