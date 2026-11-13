A colleague wrote the selection model below with the budget and nothing else, and the solver now
funds a breaker bay without the tower it sits on. The planning rules live in the `Project` records:
`must_do`, `parent` and `group` (projects sharing a group are alternatives, as in the lesson's
repair-or-replace pair).

Write `add_rules(model, x, projects)` in `selection.py`, adding one linear constraint per rule to
the MathOpt model. `x[pid]` is the binary variable for project `pid`. `build_model` and `solve`
already call it; the tests build the model, fix a plan by its variables' bounds, and ask the
solver whether that plan is allowed.

Six to ten lines.


The model to implement, with $`P`$ the projects, $`M`$ the must-do ones, $`C`$ the ones with a
parent $`p(c)`$, and $`\mathcal{G}`$ the groups (each the set of projects sharing a `group`):

```math
\begin{aligned}
\max \;& \sum_{i \in P} \text{value}_i\, x_i \\
\text{s.t. }& \sum_{i \in P} \text{cost}_i\, x_i \le B && && \text{(budget, already written)} \\
& x_i = 1 && \forall i \in M && \text{(must}_i) \\
& x_c \le x_{p(c)} && \forall c \in C && \text{(parent}_c) \\
& \sum_{i \in g} x_i \le 1 && \forall g \in \mathcal{G} && \text{(alt}_g) \\
& x_i \in \{0, 1\} && \forall i \in P
\end{aligned}
```

`add_rules` adds the three labeled families of rows.
