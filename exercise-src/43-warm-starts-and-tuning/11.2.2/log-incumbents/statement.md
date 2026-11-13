A freight company's depot-loading model is a cost-minimizing MIP solved by HiGHS, and HiGHS does not
call MathOpt callbacks (lesson 4.3.5 shows it). To date each new plan in a unit that repeats, the team reads
HiGHS's log instead. Its progress table starts after a header line containing `LpIters`; each row
ends with these columns, in order: `BestBound`, `BestSol`, `Gap`, `Cuts`, `InLp`, `Confl.`,
`LpIters`, `Time` (a time such as `0.4s`). A row may start with a one-letter source (`J`, `L`, `T`,
...) or with spaces. `BestSol` is `inf` until there is a plan. Blank lines and restart messages can
appear inside the table, and the table ends at `Solving report`.

On a long run, HiGHS stops printing `LpIters` in full once the count passes about a million and
prints it in thousands with a `k` suffix. Three rows from one such run (a 90-second, time-limited
solve of a small market-split model, through MathOpt) show the change:

```text
 T  303210   10339    125244  66.04%   0               1                100.00%      555     12   5414    895704    42.4s
    339550   10360    141291  70.97%   0               1                100.00%      554      6   4096     1003k    47.4s
 L  374863   10550    156710  75.18%   0               0.999999         100.00%      644     12   3574     1107k    53.7s
```

Read `1107k` as 1,107,000 iterations: the count to the thousand, which is as exact as the log is.
(The same run's final report gives the exact total, `LP iterations     1873361`, where the last row
printed `1873k`.)

Before you code, write down which lines are rows, which columns give a plan's work $`w`$ and
objective $`z`$, and when a row is a *new* plan: in terms of $`z`$ and the best objective
$`z_{\text{best}}`$ so far, for a minimization and for a maximization.

Write `incumbents(log, minimize=True)` in `highs_log.py`: it returns the list of
(LP iterations, objective) pairs, as floats, one per new better plan, in log order. The tests pass
small logs as lists of lines; no solver runs. About fifteen lines.
