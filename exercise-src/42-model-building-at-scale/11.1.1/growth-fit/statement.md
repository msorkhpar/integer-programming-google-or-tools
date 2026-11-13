A regional utility (fictional, like GridCap) times its model builder on four portfolio sizes this
year and wants to know two things before next year's merger quadruples the portfolio: how fast the
build time grows, and roughly how long the merged portfolio will take to build.

If the build takes about $`t = c\, n^{a}`$ seconds for $`n`$ projects, then
$`\log t = a \log n + \log c`$: a straight line in $`(\log n, \log t)`$ whose slope is the growth
exponent $`a`$ and whose intercept is $`\log c`$. Real measurements are noisy, so no line passes
through all of them; take the least-squares line, the one that makes the sum of squared vertical
distances smallest. For points $`(x_j, y_j)`$ with means $`\bar x`$ and $`\bar y`$ its slope and
intercept are

```math
a = \frac{\sum_j (x_j - \bar x)(y_j - \bar y)}{\sum_j (x_j - \bar x)^2}, \qquad \log c = \bar y - a\, \bar x
```

Write two functions in `growth.py`:

- `fit(sizes, seconds)` returns `(a, c)`, fitted as above on $`x_j = \log n_j`$ and
  $`y_j = \log t_j`$ (natural logarithms, `math.log`);
- `predict(sizes, seconds, n)` returns the fitted curve's time for `n` projects, $`c\, n^a`$.

The measurements may come in any order. The tests use made-up times, so no clock is involved. Run
the file to see a prediction. About eight lines.
