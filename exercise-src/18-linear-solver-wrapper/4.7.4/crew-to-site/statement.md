A river authority sends pump crews to flood sites. Each site needs exactly one crew; each crew
goes to at most one site; some crews are not equipped for some sites. The cost of sending a crew
to a site is a whole number of $k, given only for the allowed pairs.

Write `assign(crews, sites, cost)` in `sites.py` with `SimpleLinearSumAssignment`. `cost` maps
`(crew, site)` to the cost, for allowed pairs only. There are never fewer crews than sites. Return
`(total cost, {crew: site})`, listing only the crews that got a site, or `None` when no assignment
covers every site.

The model, with $`E`$ the allowed pairs:

```math
\begin{aligned}
\min\;& \sum_{(c,s) \in E} \text{cost}_{c,s}\, x_{c,s} \\
\text{s.t. }& \sum_{c : (c,s) \in E} x_{c,s} = 1 && \forall s && \text{(site}_s) \\
& \sum_{s : (c,s) \in E} x_{c,s} \le 1 && \forall c && \text{(crew}_c) \\
& x_{c,s} \in \{0, 1\}
\end{aligned}
```

`SimpleLinearSumAssignment` gives *every* left node a right node, so the crew rows' "at most one"
needs the trick of the lesson's second section. The tests compare your answer with a brute-force
search. About twelve lines.
