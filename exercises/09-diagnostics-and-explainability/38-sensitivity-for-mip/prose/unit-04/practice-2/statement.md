A hospital network has computed the step points of its equipment budget's value curve: a list of
`(budget, value)` pairs, sorted by budget, where the best plan's value steps up. The first pair is
the least budget any plan fits; between two pairs the value is flat. The board asks, for a budget
and an amount of extra money, what that money buys.

Write `what_extra_buys(points, budget, extra)`. It returns `None` when `budget` is below the first
point (no plan fits). Otherwise it returns a dict:

- `"gain"`: the value at `budget + extra` less the value at `budget`;
- `"steps"`: how many steps lie in the extra money, above `budget` and at most `budget + extra`;
- `"next"`: the next step above `budget`, as `(its budget, its rise over the value at budget)`,
  or `None` if there is none.

Decide first, from the definition of a step point, what the value is at a budget equal to a step
point's budget. The tests use hand-made curves. About ten lines.
