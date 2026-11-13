A regional rail line plans its works for 2027 to 2030. The model in `rail.py` has a binary
`x[pid, t]` for each project and each year `t` in its `starts`, and it already says that no project
starts twice. Two rules remain:

- **Signal blocks.** Each list in `blocks` is a block of signal upgrades that one crew commissions
  together: either every upgrade of the block is done, all starting in the same year, or none is.
- **Platforms.** `platforms` maps a platform extension to the track upgrades that can carry its
  longer trains. A platform extension may start in year `t` only if at least one of its track
  upgrades started in year `t - 1` or earlier.

Write `add_works_rules(model, x, projects, blocks, platforms)` so that the model allows exactly the
plans that keep both rules.

The model so far, with $`P`$ the projects and $`T_i`$ the start years of project $`i`$:

```math
\begin{aligned}
& x_{i,t} \in \{0, 1\} && \forall i \in P,\ t \in T_i && \text{(project } i \text{ starts in year } t\text{)} \\
& \textstyle\sum_{t \in T_i} x_{i,t} \le 1 && \forall i \in P && \text{(once}_i\text{, given)} \\
& \text{?} && && \text{(your rows)}
\end{aligned}
```

Name the remaining sets (the blocks, the years every member of a block may start in, each
platform's track upgrades) and write your rows, each with its quantifier and a label, before you
code them. Ask what a block member's variable for a year that another member cannot use must be.

A sum over a set that can be empty, such as a project's start years up to `t`, is the number 0 in
Python, and MathOpt refuses a row with no variable on either side. Skip such a row, or start the sum
from `mathopt.LinearExpression()` (lesson 6.4.1).

The tests fix every `x[pid, t]` through its bounds and ask the solver whether the model accepts the
plan, so any correct formulation passes. About fifteen lines.
