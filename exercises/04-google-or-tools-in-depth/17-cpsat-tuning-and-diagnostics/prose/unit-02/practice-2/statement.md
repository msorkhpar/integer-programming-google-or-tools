A utility plans an outage week. Its decisions are how many crews go to each district, each an
integer in a range (`variables`, for example `{"north": (2, 6)}`), and its planners keep adding
rules: caps, minimums, pairs of districts that share a depot. Each `Rule` has a name, a linear
expression over the districts, a sense (`"<="` or `">="`) and a right-hand side; `add_rule` adds
one to a CP-SAT model and returns the constraint. When a scenario has no plan at all, the planners
want to know which of their rules are to blame.

Write `clashing_rules(variables, rules)`. Return the names of the rules CP-SAT reports as
sufficient for infeasibility, or `[]` if the rules can all hold. Guard every rule with its own
flag, assume every flag, and solve with one worker.

With $`D`$ the districts, $`[l_d, u_d]`$ their ranges and $`R`$ the rules, each with coefficients
$`a_{r,d}`$, a sense and a right-hand side $`b_r`$, the model is

```math
\begin{aligned}
& y_d \in \{l_d, \dots, u_d\} && \forall d \in D && \text{(crews per district)} \\
& f_r \in \{0, 1\} && \forall r \in R && \text{(rule } r \text{ is on)} \\
& f_r = 1 \;\Rightarrow\; \textstyle\sum_{d} a_{r,d}\, y_d \;\{\le, \ge\}\; b_r && \forall r \in R && \text{(rule}_r) \\
& f_r = 1 \text{ assumed} && \forall r \in R
\end{aligned}
```

The solver reports flags by variable index; map them back to rule names. Every kind of rule needs
its flag: guard the `">="` minimums exactly as you guard the `"<="` caps. A rule added without a
flag is always on, so the solver can never name it: a clash between a minimum and a cap must
name both. About twelve lines.
