A feed mill blends ingredients into a ration. Ingredient $`j`$ costs $`c_j`$ per tonne, at most
$`u_j`$ tonnes of it are in stock, and each nutrient row $`i`$ must be met **exactly**: a tonne of
ingredient $`j`$ brings $`A_{ij}`$ units of nutrient $`i`$, and the ration needs $`b_i`$ units. The
mill wants the cheapest ration, and its LPs will grow too large to factor, so the team wants a
first-order method.

Before you code, write the model (variables with their bounds, the objective, the rows). This
model differs from the lesson's in two ways: it **minimises**, and its rows are **equalities**.

**The sign convention the tests use.** The Lagrangian is
$`L(x, y) = c^\top x + y^\top (b - A x)`$ over $`0 \le x \le u`$, with one price $`y_i`$ per
nutrient row. The plan minimises it and the prices maximise it, so the plan moves **down**
$`c - A^\top y`$ and each price moves **up** its row's shortfall $`b_i - a_i x`$. An equality row
has both sides, so its price may take either sign and is never clipped. One iteration is then

```math
\begin{aligned}
x^{k+1} &= \operatorname{clip}_{[0,\,u]}\bigl( x^k - \tau\,(c - A^\top y^k) \bigr) \\
y^{k+1} &= y^k + \sigma\,\bigl( b - A\,(2x^{k+1} - x^k) \bigr)
\end{aligned}
```

This is the lesson's iteration rewritten for a minimisation with equality rows: in the lesson's
form (maximise $`-c^\top x`$, price on the upper side), the price of an exact row is the negative of
this $`y`$, and the lesson's dual clip $`\max(0, v - \sigma b) + \min(0, v - \sigma b)`$ is just
$`v - \sigma b`$ when both sides equal $`b`$.

Write `pdhg_step(A, b, c, u, x, y, tau, sigma)` in `blend.py`: one PDHG iteration, a primal step
clipped to the bounds and then a dual step at the look-ahead point $`2x^{k+1} - x^k`$, returning
`(x_new, y_new)` as NumPy arrays. `solve`, which runs your step from zero, is given. About three
lines.
