A pipeline at a water utility solves each night's pump-scheduling MILP with several solvers before
it trusts the plan, as a correctness check. Every solver gets the same model. Each one returns a
status and an objective value. When the solvers that claim optimality disagree, something is wrong
with one of them (a solver that quietly changed the model, a bug in an adapter), and the pipeline
must say which.

Write `suspects(results, rel_tol)` in `crosscheck.py`. `results` maps a solver's name to
`(status, objective)`. Only results with status `"OPTIMAL"` are judged. Their **reference value**
$`r`$ is the median of their objectives (Python's `statistics.median`). A solver $`k`$ with objective
$`z_k`$ is a suspect when

```math
|z_k - r| > \text{rel\_tol} \cdot \max(1, |r|)
```

Return the suspects' names, sorted. With no optimal result, return an empty list.

About eight lines.
