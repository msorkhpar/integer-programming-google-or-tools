A transit agency replaces old buses within a capital budget. The board's rule: replace as many buses
as the budget allows, and among the plans that replace that many, spend the least. Many plans
replace the most buses, so a single solve could return any of them; the board wants the same answer
every time.

Write the model first. With $`B`$ the buses, $`c_b`$ the cost of bus $`b`$ and $`K`$ the budget,
pass 1 is

```math
\max \sum_{b \in B} x_b \quad \text{s.t.} \quad \sum_{b \in B} c_b\, x_b \le K \;\; \text{(budget)}, \qquad x_b \in \{0, 1\}
```

Write pass 2 in the same notation: its objective, and the row it adds (with a label) so that it
cannot give up any of pass 1's buses. Then write `replacement_plan(costs, budget)`: build the model
with MathOpt, solve both passes with HiGHS, and return the chosen ids in sorted order. Costs are
whole numbers, so a count can be held exactly.

About twelve lines.
