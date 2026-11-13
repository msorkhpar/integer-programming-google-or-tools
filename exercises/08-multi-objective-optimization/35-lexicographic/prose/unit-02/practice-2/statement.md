A water utility picks which water mains to renew this year with a MathOpt model: one binary per
main, and a budget row. It ranks two objectives: first the most leaks avoided, then the fewest
customer disruption hours. The production service runs on HiGHS, which refuses auxiliary objectives,
so the ranking must be solved by hand, and the auditors want it to give the same answer as a native
hierarchical solve such as Gurobi's `setObjectiveN` would.

Write `two_pass(model, first, second, *, first_max, second_max, abs_tol=0.0, rel_tol=0.0)`.
`first` and `second` are linear expressions over the model's variables, and `first_max` /
`second_max` say whether each one is maximized. The function solves

```math
\begin{aligned}
&\text{pass 1:} && \Gamma_1 = \operatorname{opt}_{x} \; \text{first}(x) \\
&\text{pass 2:} && \operatorname{opt}_{x} \; \text{second}(x) \;\text{ subject to }\;
\begin{cases}
\text{first}(x) \ge \Gamma_1 - \delta & \text{if first is maximized} \\
\text{first}(x) \le \Gamma_1 + \delta & \text{if first is minimized}
\end{cases} \\
&\text{with} && \delta = \max(\text{abs\_tol},\ \text{rel\_tol} \cdot |\Gamma_1|)
\end{aligned}
```

with HiGHS, each pass to a relative gap of 0, and returns the pair `(first value, second value)` of
pass 2's plan (`mathopt.evaluate_expression(expr, result.variable_values())` evaluates an expression).

Loosen the kept row by a numerical slack of $`10^{-6}`$ beyond $`\delta`$ (subtract it from a floor,
add it to a ceiling), as `lexicographic.py` does in lesson 8.2.2: a solver can report $`\Gamma_1`$ a
hair above the value of the plan it returned, and the row must not exclude that plan. The reference
does this; the tests' values are whole numbers, far apart compared with $`10^{-6}`$, so a row without
it gives the same answers on them.

Before returning, delete the kept row, so that the model has only the rows it came with. The
objective need not be restored: the reference leaves pass 2's objective in the model, because every
call sets its own objective before it solves, and the tests check only the rows.

The tests compare your pair with an enumeration of every plan of their small instances, which is the
answer a native hierarchical solve returns. About fifteen lines.
