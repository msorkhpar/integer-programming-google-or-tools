The crew-rostering search now tries strong branching. For each fractional candidate it has already
solved both children's LPs; what is left is to score the candidates and pick one.

Write `strong_choice(parent, trials, eps=1e-6)` in `strong.py`. `parent` is the node's LP value (a
maximization). `trials` maps each candidate's name to a pair `(down, up)`: the LP values of its two
children, where `None` means that child's LP is infeasible. For each candidate, the drops are

```math
\Delta^- = \text{parent} - \text{down}, \qquad \Delta^+ = \text{parent} - \text{up}
```

with a drop of $`+\infty`$ for an infeasible child (use `math.inf`). The candidate's score is

```math
\text{score} = \max(\Delta^-, \varepsilon) \cdot \max(\Delta^+, \varepsilon)
```

Return the name with the highest score; ties go to the candidate listed first in `trials`.
