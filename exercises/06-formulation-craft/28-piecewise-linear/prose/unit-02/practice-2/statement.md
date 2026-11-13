A school district orders diesel for its buses once a season. The supplier bills an order of `v`
litres on a volume-discount curve, given as breakpoints `xs` (litres, starting at 0) and `ys`
(the total bill in $), with straight lines in between:

| Litres | 0 | 20,000 | 50,000 | 80,000 |
| --- | --- | --- | --- | --- |
| Bill ($) | 0 | 30,000 | 63,000 | 87,000 |

Each extra litre is cheaper than the last band's, so the bill is concave, and the district's model
pushes it down. The district's own rule adds one more thing: **any order above `audit_above` litres
(here 30,000) must be audited** by the finance office. An order of exactly 30,000 litres, or less,
needs no audit. No order may exceed the last breakpoint.

The model in `fuel_order.py` has a continuous `volume >= 0`, a continuous `bill` (free) and a binary
`audit`. Write `add_order_rules(model, volume, bill, audit, xs, ys, audit_above)` so that the model
allows exactly the triples `(volume, bill, audit)` where the bill is the curve's value at the
volume, and every order above `audit_above` is audited. An audit on a small order is allowed (the
office may audit anything). Add whatever variables you need. The tests use other curves and audit
volumes too.

With $`(X_j, F_j)`$ the breakpoints and $`V`$ the audit volume, the model so far is

```math
\begin{aligned}
& v \ge 0, \quad b \in \mathbb{R}, \quad a \in \{0, 1\} && && \text{(litres, bill, audit)} \\
& \text{?} && && \text{(your variables and rows)}
\end{aligned}
```

The audit volume is not one of the curve's breakpoints. Think about what that means for the binaries
that say which band an order is in, and what you can do about it without changing the bill.

The tests fix the volume, the bill and the audit and ask the solver whether the model accepts the
order, so any correct formulation passes. About fifteen lines.
