A district heating model has indicator constraints such as "if boiler $`b`$ runs
($`z_b = 1`$), then $`40 \le \text{heat}_b \le 120`$". Scenario runs need to change a rule's upper
limit, and MathOpt cannot edit an indicator constraint (lesson 4.3.1): it has to be deleted and
added again.

Write `replace_upper(model, ic, new_upper)`, which replaces the indicator constraint `ic` by one
identical in every part except its upper bound, now `new_upper`, and returns the new constraint
object. "Every part" is: the indicator variable, the value that switches it on, the lower bound, the
variables and coefficients of the row, and the name. The old object must not be used afterwards,
which is why the function returns the new one. About eight lines.

Lesson 4.3.1 rebuilds an indicator constraint from its parts: `ic.terms()` gives the row's
`(variable, coefficient)` pairs, `mathopt.fast_sum(t.coefficient * t.variable for t in ic.terms())`
turns them back into an expression for `implied_expr`, and `implied_lb` and `implied_ub` take the
bounds. There is no offset to carry: MathOpt moves a constant in the row into its bounds when it
stores the constraint, so the stored expression's constant is 0. Read every part before you delete
`ic`.
