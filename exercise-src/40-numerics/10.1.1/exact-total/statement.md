A city transit agency pays its contractors in batches. Each invoice amount arrives from the
accounting system as a Python `float` in dollars with cents, such as `1249.99`, and so does the
month's budget. Before a batch is released, `fits(amounts, budget)` must say whether its total is
within the budget, exact to the cent: a total equal to the budget fits, and a total one cent over
does not.

The current `fits` adds the floats and compares, and it already refused a batch whose invoices add
up to the budget exactly. Write `fits` so that the answer never depends on how floats round. Every
amount is a whole number of cents in the accounting system, so work in integer cents: write
`to_cents(amount)` to turn one amount into its integer number of cents, and compare the sum of
those integers with the budget's.

The tests use their own amounts. About three lines.
