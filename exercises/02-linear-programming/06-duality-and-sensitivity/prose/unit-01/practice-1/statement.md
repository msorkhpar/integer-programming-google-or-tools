A city transit agency splits its maintenance money between buses, rail and ferries. Its analyst
has no solver on the laptop she brings to the board meeting, but she wants to say, with proof, "no
plan can be worth more than this". She has candidate prices for the rows and needs a function that
says what bound they prove, if any.

The agency's LP, with $`A`$ the activities, $`R`$ the rows, $`v_j`$ the value per unit of
activity $`j`$, $`a_{ij}`$ its coefficient in row $`i`$ (0 if it does not appear) and $`b_i`$ the
row's right-hand side:

```math
\max \sum_{j \in A} v_j\, x_j \quad \text{s.t.} \quad \sum_{j \in A} a_{ij}\, x_j \le b_i \;\; \forall i \in R, \qquad x_j \ge 0 \;\; \forall j \in A
```

Prices $`y_i`$ prove the bound $`\sum_{i \in R} b_i\, y_i`$ when every price is $`y_i \ge 0`$ and
they cover every activity: $`\sum_{i \in R} a_{ij}\, y_i \ge v_j`$ for every $`j \in A`$.

Write `price_bound(value, rows, prices)` in `bound.py`. `value` maps each activity to $`v_j`$;
`rows` maps each row's name to a pair `(coefficients, rhs)`, where `coefficients` maps the
activities in that row to $`a_{ij}`$; `prices` maps every row's name to $`y_i`$. Return the bound
the prices prove, or `None` when they prove nothing. Compare the cover sums with a tolerance of
`1e-9`, since prices are floats.

About eight lines.
