A wind-farm developer chooses which turbine sites to build, scored on energy produced and on
wildlife impact avoided, both to maximize. The full model takes minutes to solve, so the developer's
analysts can afford a handful of weighted solves, not a sweep of a hundred. They want every point a
weighted sum can return, each one found, none missed because its range of shares fell between two
grid values.

You get `best_for(s)`: it solves the weighted sum with share $`s`$ on the first measure and
$`1 - s`$ on the second, and returns the (first, second) values of a best option. When several
options tie it returns the one with the larger first value, and among those the one with the larger
second value. Write `supported_points(best_for)` in `hull.py`: the list of points a weighted sum can
return, sorted by first value, each once.

Two consequences of that tie rule. At $`s = 1`$ only the first value counts, so `best_for(1.0)`
returns the option with the most of the first measure and, among several with that much, the one
with the most of the second: a Pareto-optimal end, never one that only ties on the first value
(`best_for(0.0)` is the same with the roles swapped). And a point lying exactly on the straight
segment between two points you have found ties with both of them at the share where they tie;
`best_for` then returns the end with the larger first value, so no share ever returns that point.
It is supported (lesson 8.1.2), but the search cannot see it, and the reference does not list it:
the list holds the corners of the hull, each a point that some share returns.

Think in the plane first. Once you know two points $`a`$ and $`b`$ that a weighted sum returns,
which share makes them tie? If a solve at that share returns a point that scores more than both,
what does that tell you, and where can the remaining points be? If it scores no more, can any point
lie between them on the hull? Write the share as a formula in $`a`$ and $`b`$ before coding.

About fifteen lines.
