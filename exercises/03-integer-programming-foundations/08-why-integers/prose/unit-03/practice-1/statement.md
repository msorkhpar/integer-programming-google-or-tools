A port authority wants to know how many berth-repair plans its rules leave open, to judge whether
checking them one by one is realistic. Each candidate is a `Project` with a cost ($k), a `must_do`
flag, an optional `parent` and an optional `group` of alternatives.

Write two functions in `count.py`. A plan is a set of project ids, and it is **allowed** when it
keeps every row of the selection model, with $`x_i = 1`$ for each id in the plan:

```math
\begin{aligned}
\sum_{i \in P} \text{cost}_i\, x_i &\le B && && \text{(budget)} \\
x_i &= 1 && \forall i \in M && \text{(must}_i) \\
x_c &\le x_{p(c)} && \forall c \in C && \text{(parent}_c) \\
\sum_{i \in g} x_i &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g)
\end{aligned}
```

- `allowed(plan, projects, budget)` returns whether one plan keeps all four kinds of row.
- `count_allowed(projects, budget)` checks every one of the $`2^n`$ subsets of the project ids,
  from the empty set to the full set, and returns how many are allowed.

`itertools.combinations(ids, k)` gives every subset of size `k`. The tests use at most five
projects, so checking every subset is fast. About fifteen lines.
