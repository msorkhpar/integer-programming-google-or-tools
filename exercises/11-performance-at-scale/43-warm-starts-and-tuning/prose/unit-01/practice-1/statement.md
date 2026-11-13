A city transit agency re-plans its bus replacements every January. Last year's approved plan,
`old_plan`, maps each bus it replaces to a year. This year's model has one binary variable
$`x_{b,y}`$ for each bus $`b`$ and each year $`y \in W_b`$ it may now be replaced in, given as
`windows[b]`. The year `first_year` has just begun: the replacements planned for it are under way,
so they are commitments, not decisions. Some buses are new to the list this year, and some old years
are no longer allowed (a supplier moved a delivery).

Before you code, write the rule in this notation: for each $`b`$ and $`y \in W_b`$, what value
$`\hat x_{b,y}`$ the start gives, in terms of last year's year $`s_b`$ (when $`b`$ was in the old
plan) and the first year $`y_0`$; and which buses form the committed set.

Write two functions in `fleet.py`:

- `committed(old_plan, first_year)` returns the set of buses last year's plan replaces in
  `first_year`.
- `carry_forward(old_plan, windows, first_year)` returns a complete start: a dict with one value,
  1.0 or 0.0, for every `(bus, year)` of `windows`. It keeps last year's decision wherever this
  year's model can still express it, and gives no other year a 1.

`windows` may still list a committed bus (one replaced in `first_year`), even with `first_year`
among its years. That bus is already being replaced, so it is not a decision to hint: the start gives
it 0.0 in every year of its window. Only a replacement planned after `first_year` is carried
forward as a 1.

The tests call your functions with small plans; no solver runs. About ten lines.
