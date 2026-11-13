A water utility trades leak reduction (megaliters a year) against the cost of its pipe-repair
program (whole $k). Its model is wrapped as `solve_at(ceiling)`: the plan with the most leak
reduction among plans costing at most `ceiling`, returned as `((leak_cut, cost), slack)` with
`slack = ceiling - cost`, or `None` when no plan is that cheap. Costs always come in multiples of
`step`.

This is the lesson's sweep turned upside down: the floored objective is one to keep *low*, so the
row is a ceiling, and the sweep starts at the top (`high`) and lowers the ceiling. Write
`exact_sweep(solve_at, low, high, step)` in `leaks.py`. It returns every different plan, in the
order found. Never ask about a ceiling whose answer the last slack already tells you, never ask
again after a ceiling that returned `None`, and ask no ceiling below `low`.

Start at `high` even when it is not a multiple of `step`; the reference does, and the tests check it.
Every ceiling you ask is then `high` minus whole steps. Because costs are multiples of `step`, a
ceiling that falls between two multiples admits exactly the plans the multiple just below it
admits, so it returns the same plan, and the slack, measured from the ceiling you asked, still tells
you how many whole steps to skip.

Work out first, on paper: after a plan with slack `s`, which ceilings would return the same plan,
and so which ceiling to ask next. The tests pass a `solve_at` that counts its calls. About six lines.
