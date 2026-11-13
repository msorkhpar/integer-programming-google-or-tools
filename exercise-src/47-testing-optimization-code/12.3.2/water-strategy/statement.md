The water utility's property tests (practice 1) need instances to run on, and a random instance is
often useless: a must-do that costs more than the budget makes the whole instance infeasible, and
then there is no plan to check. Write a Hypothesis strategy whose every instance has a valid plan.

The rules are the selection's of practice 1: with $`y_p \in \{0,1\}`$,

```math
\begin{aligned}
& \sum_{p} a_p\, y_p \le A && \text{(capital)} \\
& \sum_{p} o_p\, y_p \le O && \text{(operating)} \\
& y_p = 1 && \forall p \in M \quad \text{(must}_p) \\
& y_p \le y_q && \forall p \in P,\ q \in N_p \quad \text{(needs}_{p,q})
\end{aligned}
```

Write `instances()` in `water_strategy.py`, a `@st.composite` strategy returning the dict described
in its docstring, with project names of your choice. Each instance must have:

- one to six projects, and every project a key of `cost`, `needs` and `value`;
- capital costs of 1 to 40, operating costs of 1 to 10, and values of 1 to 20;
- at most two prerequisites per project, each another project, and no chain of prerequisites that
  leads back to where it started;
- must-dos, and budgets, such that some plan meets all four rules;
- budgets that are sometimes tight: across the drawn instances, funding every project at once must
  sometimes break a budget.

The tests draw 150 instances with a fixed seed and check each condition. About fifteen lines.
