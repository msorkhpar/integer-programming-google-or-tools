A transit agency plans next year's bus-fleet upgrades with two ranked objectives: first the most
riders served (thousands of trips), then the most emissions cut (tonnes). Its analyst has already run
the lexicographic solve once per allowance in a sweep: each run let riders served fall by at most
`allowed` below the best value, `best`, and reported the plan's riders served (`first`) and emissions
cut (`second`).

The board does not want the raw sweep. It wants the **steps**: the allowances at which the plan
actually gets better on emissions, and what each step costs and buys.

Write `steps(best, sweep)`. `sweep` is a list of `(allowed, first, second)` tuples, in any order,
and always includes the row with `allowed == 0`. Return a list of `(allowed, taken, gain)` tuples,
one per step, in increasing order of `allowed`:

- a row is a step if its `second` is larger than the `second` of every row with a smaller
  allowance; a row that reaches no more than an earlier row is the same plan bought at a higher
  price, and is left out;
- `taken` is the riders served the plan gave up, `best - first`;
- `gain` is the emissions cut beyond the zero-allowance row's `second`.

The zero-allowance row is always the first step, with a gain of 0. About ten lines.
