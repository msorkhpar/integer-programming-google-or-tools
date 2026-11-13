A city's parks department (not GridCap) picks improvements for one park within a budget. Some
improvements need another one (`requires`: `(a, b)`, a needs b) and some pairs exclude each other
(`excludes`: `(a, b)`). The department's analyst wants the model in both CP-SAT and MathOpt, to check
one against the other before choosing a solver.

Write two functions in `twins.py`, each returning the best total value as an `int`:

- `best_with_cpsat(value, cost, budget, requires, excludes)`: the model in CP-SAT, with the two rules
  written as logic constraints;
- `best_with_highs(value, cost, budget, requires, excludes)`: the same model in MathOpt, with the
  rules as linear rows, solved with HiGHS.

The model, with $`I`$ the improvements and $`x_i \in \{0, 1\}`$ "improvement $`i`$ is built":

```math
\begin{aligned}
\max \;& \sum_{i \in I} v_i\, x_i \\
\text{s.t. }& \sum_{i \in I} c_i\, x_i \le \text{budget} && \text{(budget)} \\
& x_a \Rightarrow x_b && \forall (a, b) \in \text{requires} \\
& \lnot x_a \lor \lnot x_b && \forall (a, b) \in \text{excludes}
\end{aligned}
```

The tests compare each function with a brute-force search. About twenty lines in all.
