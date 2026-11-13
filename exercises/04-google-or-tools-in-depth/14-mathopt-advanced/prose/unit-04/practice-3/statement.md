A telecom operator chooses which towers to upgrade, with an integer $`u_k \in \{0, \dots, U_k\}`$ per
tower $`k`$ (how many radios it gets). Management keeps asking "what is the best plan if we leave
these towers alone?". In the model that is

```math
u_k \le 0 \qquad \forall k \in \text{ruled out}
```

for that one question only.

Write `objective_without(model, variables, solver)`. It sets the upper bound of every variable in
`variables` to 0, solves `model` with `mathopt.solve(model, solver)`, and returns the optimal
objective value. Whatever happens, the model must be exactly as before when the function returns:
each variable's upper bound back to *its own* old value, and nothing deleted. If the solve raises,
the error should still reach the caller, with the bounds already restored. About eight lines.
