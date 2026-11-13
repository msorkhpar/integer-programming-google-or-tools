A water utility selects which mains to replace this year, and its selection code is about to be
rewritten. Before the rewrite, the team wants property-based tests that would notice if the new code
broke a business rule. You write the three properties; the tests run them under Hypothesis.

An instance has projects $`P`$, each with a capital cost $`a_p`$ and an operating cost $`o_p`$, a
capital budget $`A`$ and an operating budget $`O`$, must-do projects $`M \subseteq P`$, and for each
project a set $`N_p`$ of prerequisites, projects that must be funded whenever $`p`$ is. The
selection, with $`y_p \in \{0, 1\}`$ and $`v_p`$ the project's value, is

```math
\begin{aligned}
\max\ & \sum_{p \in P} v_p\, y_p \\
\text{s.t. } & \sum_{p} a_p\, y_p \le A && \text{(capital)} \\
& \sum_{p} o_p\, y_p \le O && \text{(operating)} \\
& y_p = 1 && \forall p \in M \quad \text{(must}_p) \\
& y_p \le y_q && \forall p \in P,\ q \in N_p \quad \text{(needs}_{p,q})
\end{aligned}
```

The docstring of `water_properties.py` gives the instance's dict shape; a plan is the set of funded
projects. Write the three functions. Each returns `None` when its property holds for the plan and
fails an `assert` when it does not:

- `within_both_budgets`: the plan's spend fits both budgets;
- `must_dos_funded`: every must-do is in the plan;
- `prerequisites_funded`: no funded project lacks any of its prerequisites.

Check the plan against the instance's data, not against a solver. The tests draw instances that are
feasible by construction and run each property, as the body of a Hypothesis test, on the plans of
a correct solver (it must hold on every one) and of solvers that break a rule (it must fail on
some). Ties between equal plans do not matter. About eight lines.
