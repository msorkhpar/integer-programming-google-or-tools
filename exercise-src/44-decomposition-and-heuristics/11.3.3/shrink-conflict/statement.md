A transmission utility books one mobile crane for its substation lifts. A scheduling check,
`fits(lifts)`, answers whether a set of lifts can all be booked in one month (it is given, and its
inside does not matter here). When a month's set is refused, the planning master needs a no-good
cut: "not all of these lifts in this month". The fewer lifts the cut names, the more plans it
rules out, so the planners want the refused set shrunk to a **core**: a subset that `fits` still
refuses, from which no single lift can be dropped without `fits` accepting the rest.

Write first what the cut on a core $`S`$ says in the master's variables $`x_{l,m}`$ (lift $`l`$ in
month $`m`$), and why it is valid for every plan. Then write `shrink(lifts, fits)` to return a core
of the refused list `lifts`, as a list in the input's order. Try each lift once, in order.

About six lines.
