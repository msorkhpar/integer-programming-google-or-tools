A port's maintenance team fills each shift's dredging hours with standard jobs: job type $`j`$
takes $`a_j`$ hours and removes $`c_j`$ units of silt, and any whole number of each type may be
scheduled. With $`d`$ hours, the most silt removed is
$`z(d) = \max \{ \sum_j c_j x_j : \sum_j a_j x_j \le d,\ x_j \in \mathbb{Z}_{\ge 0} \}`$.

A planner proposes a **price function** $`F`$ on the hours $`0, 1, \dots, D`$ and claims that
$`F(b)`$ bounds the silt any schedule removes in $`b`$ hours. Lesson 9.2.1 gave the conditions
under which that claim holds for a maximization with one $`\le`$ row: $`F`$ must be dual feasible
for the subadditive dual. Write each condition in symbols first, for this problem, with its
quantifier: what $`F(0)`$ must be, what one unused hour may be worth, how $`F`$ must treat a sum
of two amounts of hours, and what it must give each job type.

Then write `is_dual_feasible(F, hours, silt)`. `F` is a list with `F[d]` for $`d = 0..D`$
(`D = len(F) - 1`), and `hours` and `silt` hold $`a_j`$ and $`c_j`$ (each $`a_j \le D`$). Return
`True` when `F` meets every condition, `False` otherwise. Compare with a tolerance of `1e-9`,
because a linear price is a float.

The tests build price functions by hand, valid and not. About ten lines.
