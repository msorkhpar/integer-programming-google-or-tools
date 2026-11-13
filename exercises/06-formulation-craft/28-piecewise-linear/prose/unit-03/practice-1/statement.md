A county expands its wastewater treatment plant this decade in stages, given in `widths` as the
capacity each stage adds (ML/day), in order: for example 4, 3 and 5. The engineers' rule is that
**a stage may not begin until the stage before it is finished**. A stage may be left part built
(the plan can stop anywhere inside a stage), and nothing need be built at all.

The model in `expansion.py` has a continuous `built[k]` per stage, between 0 and `widths[k]`: how
much of stage `k`'s capacity the plan builds. Write `add_stage_order(model, built, widths)` so that
the model allows exactly the plans that respect the rule. Add whatever variables you need. The
tests use other widths too.

With $`k = 1, \dots, K`$ the stages and $`W_k`$ their widths, the model so far is

```math
\begin{aligned}
& 0 \le u_k \le W_k && k = 1, \dots, K && \text{(capacity built in stage } k\text{, ML/day)} \\
& \text{?} && && \text{(your variables and rows)}
\end{aligned}
```

No curve is involved, but the rule is one you have seen: the order in which segments are used.
Watch the units: `built[k]` is in ML/day, not a share of the stage.

The tests fix every stage's `built` value and ask the solver whether the model accepts the plan, so
any correct formulation passes. About five lines.
