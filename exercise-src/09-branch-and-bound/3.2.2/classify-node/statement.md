A warehouse-siting search (open a site or not, 0-1 variables, maximize the yearly saving) has just
solved one node's LP. The loop needs to know what to do with the node.

Write `classify(status, bound, integral, incumbent, whole_values=False)` in `classify.py`.

- `status` is `"optimal"` or `"infeasible"`;
- `bound` is the node's LP value (ignore it when the LP is infeasible);
- `integral` says whether the LP solution is all 0 and 1;
- `incumbent` is the best plan's value so far, or `None` before the first plan;
- `whole_values` says that every plan is worth a whole number.

Return one of `"infeasible"`, `"bound"`, `"incumbent"` or `"branch"`, with the tests in this order:

```math
\begin{aligned}
&\text{infeasible} && \text{if the LP has no solution} \\
&\text{bound} && \text{if } b \le \underline{z}, \text{ where } b = \lfloor \text{bound} \rfloor \text{ when whole\_values, else } b = \text{bound} \\
&\text{incumbent} && \text{if the LP solution is integral (it becomes the new incumbent)} \\
&\text{branch} && \text{otherwise}
\end{aligned}
```

where $`\underline{z}`$ is `incumbent`; with no incumbent, the bound test never prunes.

Round down with a small guard, as the lesson's `can_beat` does with `math.floor(bound + EPS)`: an
LP value a solver returns as 101.9999999999 for a true 102 must count as 102, not 101. The reference
solution uses `math.floor(bound + 1e-9)`; the lesson's `EPS` of `1e-6` passes the tests too. With
`whole_values` false, the reference compares `bound` unrounded and with no guard.
