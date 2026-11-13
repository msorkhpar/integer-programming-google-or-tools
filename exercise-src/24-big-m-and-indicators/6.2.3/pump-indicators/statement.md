A water utility's booster station has one pump. When the pump is idle it moves no water. When it
runs, it must move at least `min_flow` (below that it overheats). The station's records give no
rated maximum flow, so the flow variable has no upper bound: $`0 \le f`$, nothing more.

`pump_variables` (given) creates the flow $`f`$ and the on/off binary $`u`$. Write
`add_pump_rules(model, flow, on, min_flow)` in `pump.py`, with MathOpt indicator constraints, so
that the model needs no $`M`$. The tests solve with SCIP (`mathopt.SolverType.GSCIP`), which takes
indicator constraints.

The model so far, with $`q`$ the minimum flow:

```math
\begin{aligned}
& f \ge 0, \quad u \in \{0, 1\} && \\
& \text{?} && \text{(idle\_moves\_nothing)} \\
& \text{?} && \text{(running\_minimum)}
\end{aligned}
```

Write each rule as an implication first ("$`u = \dots \Longrightarrow \dots`$"), then code it. Before
running the tests, decide what a big-M version of the idle rule would need that this model does not
have.

The tests fix a plan by its variables' bounds and ask SCIP whether it is allowed, so any correct
pair of rules passes. Two lines.
