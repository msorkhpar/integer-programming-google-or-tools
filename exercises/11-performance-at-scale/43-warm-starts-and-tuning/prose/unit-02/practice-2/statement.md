An airline's crew-pairing team tries one solver setting at a time on a fixed set of models and
seeds, and records two measures per run, paired with the default's run on the same model and seed:
the work until a good plan was found, and the work to prove optimality. They want one word per
setting, decided by a written rule, not by whoever reads the table.

For one measure, with paired work $`a_k`$ (new setting) and $`b_k`$ (default), $`k = 1..n`$, let
$`r = \text{SGM}_s(a) / \text{SGM}_s(b)`$ (the shifted geometric mean of lesson 5.4.2, given in the
starter as `sgm`), $`W`$ the number of $`k`$ with $`a_k < b_k`$ and $`L`$ the number with
$`a_k > b_k`$. Before you code, write the rule as inequalities on $`r`$, $`W`$, $`L`$ and a margin
$`m`$: a measure is *better* when the ratio is at least $`m`$ below 1 and the wins outnumber the
losses, *worse* in the mirror case, and *same* otherwise. "At least" includes the edge: a ratio of
exactly $`1 - m`$ can be *better* (the test is $`r \le 1 - m`$, not $`<`$), and a ratio of exactly
$`1 + m`$ can be *worse* ($`r \ge 1 + m`$). Then write how two judgements combine:
better and worse is a *trade-off*; better with no worse is *adopt*; worse with no better is
*reject*; anything else is *no effect*.

Write `judge(new, old, shift, margin)` (returns `"better"`, `"worse"` or `"same"`) and
`verdict(plan_new, plan_old, proof_new, proof_old, shift, margin=0.05)` (returns `"adopt"`,
`"reject"`, `"trade-off"` or `"no effect"`) in `verdict.py`. The tests pass lists of numbers; no
solver runs. About fifteen lines.
