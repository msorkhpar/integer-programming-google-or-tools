A freight company plans its fleet with two prioritized objectives and solves them one at a time,
because its solver does not take auxiliary objectives. After each objective $`f`$ is optimized to
its best value $`\Gamma`$, a row must keep $`f`$ within its allowed loss of $`\Gamma`$ for every
later solve. With the tolerances of a `mathopt.ObjectiveParameters` (either may be `None`):

```math
\text{loss} = \max\big(\text{absolute},\; \text{relative} \cdot |\Gamma|\big), \qquad
\begin{cases}
f(x) \ge \Gamma - \text{loss} & \text{if } f \text{ is maximized} \\
f(x) \le \Gamma + \text{loss} & \text{if } f \text{ is minimized}
\end{cases}
```

A missing tolerance counts as 0, and `params=None` means a loss of 0.

Write `keep_within(model, expr, best, is_maximize, params)`, which adds that row to `model` for the
linear expression `expr` and returns it. The tests fix the variables and ask HiGHS whether the model
accepts the values, so any correct row passes. About eight lines.
