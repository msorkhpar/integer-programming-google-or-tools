A university plans roof work on its buildings for 2027 to 2036. Each roof has two candidate
projects, a **patch** and a **replacement**, and the model in `roofs.py` has a binary
`patch[r, s]` for each year `s` the roof may be patched and `replace[r, t]` for each year `t` it
may be replaced. Each project happens at most once (that row is given). The engineers' rules:

- A roof may be patched, replaced, both, or neither.
- A patch buys time: a replacement may follow a patch only if it starts at least `gap` years after
  the patch (a patch in 2028 and a replacement in 2028 + `gap` is fine).
- A new roof comes with a warranty: the roof may not be patched in its replacement year, nor in the
  `warranty` years after it. A patch later than that is allowed (a replacement in 2029 with a
  warranty of 3 rules out patches in 2029 to 2032).

Write `add_sequence_rules(model, patch, replace, roofs, gap, warranty)`, where `roofs` maps each roof
to a pair `(patch_years, replace_years)`, so that the model allows exactly the plans that keep the
rules.

The model so far, with $`R`$ the roofs, $`S_r`$ and $`T_r`$ roof $`r`$'s patch and replacement
years:

```math
\begin{aligned}
& p_{r,s} \in \{0, 1\},\ q_{r,t} \in \{0, 1\} && \forall r \in R,\ s \in S_r,\ t \in T_r && \text{(patch in } s\text{, replace in } t\text{)} \\
& \textstyle\sum_{s} p_{r,s} \le 1,\ \sum_{t} q_{r,t} \le 1 && \forall r \in R && \text{(once, given)} \\
& \text{?} && && \text{(your rows)}
\end{aligned}
```

For a replacement in year $`t`$, list the patch years that conflict with it, then write one row per
roof and replacement year, with its quantifier and a label, before you code it. Check your list
against the two examples in the rules.

The tests fix every variable through its bounds and ask the solver whether the model accepts the
plan, so any correct formulation passes. About six lines.
