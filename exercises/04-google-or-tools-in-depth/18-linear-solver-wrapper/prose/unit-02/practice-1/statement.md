A storm-response depot plans its crews with an old pywraplp script, `legacy_plan(data)` in
`staffing.py`. The planning service is moving to MathOpt. Write `mathopt_plan(data)`: the same model
in MathOpt, solved by SCIP, returning what `legacy_plan` returns: `("OPTIMAL", cost, {variable
name: value})`, or `(reason name, None, None)` when the solve is not optimal (use
`result.termination.reason.name`).

Read the legacy function first; it is the specification. Its model, with $`K`$ the crew kinds:

```math
\begin{aligned}
\min\;& \sum_{k \in K} c_k\, n_k + r\, o \\
\text{s.t. }& L \le \sum_{k \in K} h_k\, n_k + o \le U && \text{(cover)} \\
& n_k \in \{m_k, \dots, \bar n_k\} \text{ integer} && \forall k \in K \\
& 0 \le o \le \bar o
\end{aligned}
```

$`n_k`$ is the number of crews of kind $`k`$, each covering $`h_k`$ hours at cost $`c_k`$, between
the union minimum $`m_k`$ and the most available $`\bar n_k`$; $`o`$ is overtime hours at rate $`r`$
per hour, at most $`\bar o`$; the depot needs between $`L`$ and $`U`$ hours covered. Keep the
variable names the old script uses (`crews_<kind>`, `overtime`).

The tests run both functions on several depots and check that they agree on the status, the cost
and the variables reported. About fifteen lines.
