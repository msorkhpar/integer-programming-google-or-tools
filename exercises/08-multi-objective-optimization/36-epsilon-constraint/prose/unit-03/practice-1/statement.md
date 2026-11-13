A county library system has a budget for branch upgrades. Each upgrade adds opening hours per week
and reading-room seats, both whole numbers, and has a cost. The board wants to see every choice
worth considering: the full list of (hours, seats) scores that no other affordable choice beats on
both or ties on one and beats on the other.

Write `frontier(upgrades, budget)` in `libraries.py`. It returns every Pareto-optimal score as a
list of `(hours, seats)` pairs, sorted by hours (fewest first), each listed once. The starter builds
the model, its budget row and the two objective expressions; you write the generator. Use any
method from the lesson; whichever you pick, make sure a tie on one objective cannot leave a
dominated score in the list.

If you pick AUGMECON (a seats floor with a slack, and a reward $`(\rho / r_2) \cdot s`$ on the
slack, as in lesson 8.3.2), you need $`r_2`$. A lexicographic payoff table gives the exact range of
seats, which bounds every slack when the first floor is the seats of the most-hours end, as in
lesson 8.3.2. Any number at least as large as every slack your sweep can produce works as well, for
example the total seats of all upgrades, which also covers a sweep that starts its floor at 0. With such an $`r_2`$, $`s / r_2 \le 1`$, so the reward is
at most $`\rho`$ ($`10^{-3}`$ in the lesson), less than one hour; hours are whole numbers, so the
reward can never pay for an hour and only chooses among choices tied on hours. Too small an
$`r_2`$ breaks that: the reward can then outweigh an hour and trade hours for seats. The reference
needs no $`r_2`$: at each floor it maximizes hours, then holds the hours and maximizes seats, two
solves per floor.

Write down first what you solve at each floor (objective, floor row, any tie-breaking), and why it
cannot miss a score. The tests list every affordable choice by hand and check your list against it,
including that no score in it dominates another. About fifteen lines.
