A substation-upgrade model has binaries $`x_j`$, and an LP solver you can call with some of them
fixed. Write the dive that turns LP points into a plan.

Write `dive(lp)` in `dive.py`. `lp` is a function: `lp(fixed)` takes a dict from variable to 0 or 1
and returns the LP optimum with those variables fixed, as a dict from every variable to its value,
or `None` when that LP has no solution. Repeat:

1. Call `lp(fixed)`, starting with `fixed = {}`. If the point has no fractional variable (every value
   within $`10^{-6}`$ of 0 or 1), return `(plan, steps)`: `plan` maps each variable to its value
   rounded to 0 or 1.
2. Otherwise pick the fractional variable with the smallest $`\min(x_j, 1 - x_j)`$ (ties by name),
   and set `target` to 1 if $`x_j \ge 0.5`$, else 0.
3. Call `lp` with `fixed` plus $`x_j`$ = `target`. If that returns `None`, use the other value
   instead. Add the fixing to `fixed`, record `(variable, value)` in `steps`, and go back to step 1
   with the point you got.

If both values of a variable give `None`, return `(None, steps)`. A failed fixing is not a step:
`steps` holds only the fixings that were kept, so the variable whose two values both failed is not
in it. The reference solution appends to `steps` only after a call returns a point. The tests give you an `lp` that
answers only the calls a correct dive makes.
