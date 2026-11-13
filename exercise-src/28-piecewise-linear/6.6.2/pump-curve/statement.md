A water utility models the electricity drawn by a booster pump station as a function of the flow it
delivers. The pump's measured curve is given as breakpoints `xs` (flow, L/s, starting at 0) and `ys`
(power, kW), with straight lines in between:

| Flow (L/s) | 0 | 20 | 40 | 60 | 80 |
| --- | --- | --- | --- | --- | --- |
| Power (kW) | 0 | 30 | 42 | 70 | 120 |

The pump is most efficient in the middle band, so the slopes fall and then rise: the curve is
neither convex nor concave. The station's model uses the power in two places, as a cost in the
energy bill and as a load that a backup generator must be able to carry, so the power is pushed
down in one row and up in another. The pump cannot deliver more than the last breakpoint's flow.

The model in `booster.py` has two continuous variables, `flow >= 0` and `power` (free). Write
`add_power_curve(model, flow, power, xs, ys)` so that the model allows exactly the pairs
`(flow, power)` that lie on the curve. Add whatever variables you need. The tests use other curves
too.

With $`(X_j, F_j)`$, $`j = 0, \dots, K`$, the breakpoints, the model so far is

```math
\begin{aligned}
& q \ge 0 && && \text{(flow, L/s)} \\
& p \in \mathbb{R} && && \text{(power, kW)} \\
& \text{?} && && \text{(your variables and rows: } p = f(q)\text{)}
\end{aligned}
```

Neither push nor shape helps here, so every point must be tied to one segment. The lesson's lambda
form is one way; any formulation that allows exactly the curve's points passes.

The tests fix the flow and the power and ask the solver whether the model accepts the pair, so any
correct formulation passes. About ten lines.
