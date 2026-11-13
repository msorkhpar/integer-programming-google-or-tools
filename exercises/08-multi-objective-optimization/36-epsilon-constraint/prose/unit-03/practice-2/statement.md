A state forestry agency has generated the frontier of its wildfire fuel-reduction plans: each plan
is scored `(homes, left)`, the homes protected and the budget left unspent ($k), and both are worth
having. The agency's board will not pay more than `max_price` $k of unspent budget per extra home
protected, for any step.

Write `go_until(points, max_price)` in `wildfire.py`. Starting from the plan with the most budget
left, walk toward more homes along the supported plans only (the starter's `upper_hull` returns
them, fewest homes first), and take each step whose price, $k given up per extra home, is at most
`max_price`. Stop before the first step that costs more. Return the plan you stop at.

`upper_hull` keeps a plan that lies exactly on the straight segment between two others: a weighting
that ties the two ends ties it too, so it is supported (lesson 8.1.2's definition). The two steps
into and out of it have the same price, so the walk takes both or neither.

The tests use their own frontiers, with unsupported plans among the points. About six lines.
