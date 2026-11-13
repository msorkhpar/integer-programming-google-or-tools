A water utility relines old cast-iron pipes with a cured-in-place resin liner. The lining contractor
sets up for **one** liner thickness `t` (in mm) for the whole program, chosen between `t_low` and
`t_high`; every pipe relined this year gets that thickness.

- Relining pipe `p` at thickness `t` uses `kg_per_mm * t` kilograms of resin; a pipe that is not
  relined uses none. The resin used by the whole program must not exceed `supply` kilograms.
- Each pipe has a structural minimum `min_mm`: if the pipe is relined, the program's thickness must
  be at least that minimum. A pipe that is not relined sets no minimum.

The model in `relining.py` has a binary `x[pid]` per pipe (1 if relined) and a continuous `t`
between `t_low` and `t_high`. Write `add_liner_rules(model, x, t, pipes, t_low, t_high, supply)` so
that the model allows exactly the plans (which pipes, and which thickness) that keep both rules. Add
whatever variables you need.

With $`P`$ the pipes, $`m_p`$ the resin per mm of pipe $`p`$ (kg) and $`d_p`$ its minimum thickness
(mm), the model so far is

```math
\begin{aligned}
& x_p \in \{0, 1\} && \forall p \in P && \text{(reline pipe } p\text{)} \\
& t_{\text{low}} \le t \le t_{\text{high}} && && \text{(liner thickness, mm)} \\
& \text{?} && && \text{(your variables and rows)}
\end{aligned}
```

The resin of one pipe is a product of a binary and a continuous variable. Write it, replace it by a
new variable with its domain and rows, and decide which of those rows the supply row really needs.
Use the bounds the data gives you.

The tests fix both which pipes are relined and the thickness, and ask the solver whether the model
accepts the plan, so any correct formulation passes. About eight lines.
