A transmission operator (not GridCap) must add at least `need` MWh of battery storage to its grid
before next winter. Each candidate site can host one battery of a fixed size: site $`s`$ adds
$`m_s`$ MWh, a whole number of at least 1, and costs $`c_s`$ ($k). A site is built once or not at
all. The planners want the **cheapest** set of sites whose storage adds up to **at least** the
need; more than the need is fine.

Written as a model, with $`S`$ the candidate sites and $`N`$ the need, this is

```math
\begin{aligned}
\min \;& \sum_{s \in S} c_s\, x_s \\
\text{s.t. }& \sum_{s \in S} m_s\, x_s \ge N && \text{(need)} \\
& x_s \in \{0, 1\} && \forall s \in S
\end{aligned}
```

a knapsack turned around: minimize instead of maximize, and the row is "at least". You will not
solve it with a MILP solver. Write `cheapest_cover(sites, need)` in `storage.py` as a dynamic
program over MWh amounts, the way the lesson's table runs over budget amounts. It returns
`(least cost, [names of one cheapest set])`, the names in the order the sites were given, or `None`
when even every site together adds less than `need`. A need of 0 is met by building nothing, so it
returns `(0, [])`.

Before coding, decide on paper what one table entry means here (the lesson's `best[b]` was "the most
value within $`b`$"), how a new site updates it, and what happens to an amount above the need.

The tests use their own small sets of sites and check the cost and that the named sites really reach
the need. About fifteen lines.
