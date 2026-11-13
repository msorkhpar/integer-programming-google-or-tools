A water utility rounds the LP relaxation of its main-replacement model and wants to know, before
anyone reads the rounded plan, which of the model's rows it breaks. Each candidate is a `Project`
with a cost and a value ($k), a `must_do` flag, an optional `parent` (the project it depends on)
and an optional `group` (a set of alternatives, at most one of which may be funded).

Write `broken_rows(plan, projects, budget)` in `rows.py`. `plan` is the set of funded project ids.
With $`P`$ the projects, $`M`$ the must-do ones, $`C`$ the ones with a parent $`p(c)`$, and
$`\mathcal{G}`$ the groups, the rows are:

```math
\begin{aligned}
\sum_{i \in P} \text{cost}_i\, x_i &\le B && && \text{(budget)} \\
x_i &= 1 && \forall i \in M && \text{(must}_i) \\
x_c &\le x_{p(c)} && \forall c \in C && \text{(parent}_c) \\
\sum_{i \in g} x_i &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g)
\end{aligned}
```

where $`x_i`$ is 1 if $`i`$ is in `plan` and 0 otherwise. Return the set of labels of the rows the
plan breaks: `"budget"`, `"must_<pid>"`, `"parent_<pid>"` (the child's id) and `"alt_<group>"`.
An allowed plan returns an empty set.

About a dozen lines: one check per row, in the model's order.
