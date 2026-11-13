A hospital's finance office swept its maintenance LP over the equipment budget once, re-solving at
many budgets, and stored the result as segments: on each interval of the budget the optimal value
rises at a constant shadow price. Department heads now send requests like "+$30k" or "cut $20k",
and the office wants the exact change in value for each, without re-solving every time.

The sweep is a list of segments `(start, end, price)`, sorted and contiguous: each segment's `end`
is the next one's `start`. Between `start` and `end` the optimal value $`z(r)`$ has slope `price`,
so the change from $`r`$ to $`r + \Delta`$ is the sum, over the segments the move passes through,
of the price times the length covered:

```math
z(r + \Delta) - z(r) \;=\; \sum_{\text{segments } (s, e, p)} p \cdot \big|\,[s, e] \cap [r, r + \Delta]\,\big|
\qquad (\Delta \ge 0)
```

with the sign reversed for a cut ($`\Delta < 0`$): the value falls by the same sum taken over
$`[r + \Delta, r]`$.

Write `value_change(segments, rhs, delta)` in `change.py`. Return the change in the optimal value
when the budget moves from `rhs` to `rhs + delta`, or `None` when `rhs + delta` lies outside the
swept interval (before the first `start` or after the last `end`). `rhs` itself is always inside it.

About ten lines.
