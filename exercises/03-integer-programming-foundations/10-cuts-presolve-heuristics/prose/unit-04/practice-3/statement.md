GridCap's nightly job must decide, from the two bounds a solver reports, whether a run met the
planners' tolerance, the same way HiGHS does when it prints `Status Optimal`.

Write `verdict(primal, dual, tolerance, sense, integral)` in `verdict.py`. `primal` is the
incumbent's value, `dual` the bound, `sense` is `"max"` or `"min"`, and `integral` says whether every
plan's value is a whole number. First, when `integral` is true, round the bound toward the
incumbent: down to a whole number for `"max"`, up for `"min"` (allow $`10^{-9}`$ for float noise,
so 50002.0000000001 counts as 50002). Then

```math
\text{gap} = \frac{\lvert \text{dual} - \text{primal} \rvert}{\lvert \text{primal} \rvert}
```

and return the pair `(gap, gap <= tolerance)`.
