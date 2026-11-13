A vegetation contractor's crew works a whole number of hours a week, from 0 to 60. The union
agreement sets the rules: without approved overtime, a crew works at most 40 hours. With overtime
approved, it may work up to 55 hours, and the contractor only approves overtime for a week of at
least 45 hours (below that, the paperwork is not worth it).

`crew_variables` (given) creates the hours, an integer variable, and `overtime`, a Boolean. Write
`add_hours_rules(model, hours, overtime)` in `crew_hours.py` with CP-SAT enforcement literals, so
that no row needs an $`M`$.

The model so far, with $`w`$ the hours and $`o`$ the overtime literal:

```math
\begin{aligned}
& w \in \{0, 1, \dots, 60\}, \quad o \in \{\text{false}, \text{true}\} && \\
& \text{?} && \text{(your rows, each with the literal that enforces it)}
\end{aligned}
```

Write each rule as "row, enforced if literal" first, then code it. Check your rows against a week of
50 hours with and without overtime.

The tests fix the hours and the overtime literal and ask CP-SAT whether the week is allowed, so any
correct set of rows passes. Three lines.
