The water utility's analysts keep a fallback for the day the MILP solve is unavailable: round the
LP relaxation down, then spend what is left. They want it written once and tested.

Write `round_down_and_fill(shares, projects, budget)` in `fill.py`. `shares` maps each project id
to its value $`x_i`$ in the LP relaxation's answer ($`0 \le x_i \le 1`$). The function returns the
set of funded ids, built in two steps:

1. **Round down.** Keep every project whose share is 1. A solver returns floating-point numbers, so
   treat any share greater than $`1 - 10^{-6}`$ as 1.
2. **Fill.** Walk through all projects in decreasing order of $`\text{value}_i / \text{cost}_i`$,
   once. Add a project not yet in the plan if all three hold: the plan's cost stays
   $`\le B`$; its `parent`, if it has one, is already in the plan; and no other project of its
   `group`, if it has one, is already in the plan.

The result keeps every row of the model in the *Name the rows a rounded plan breaks* practice: the
LP's whole projects already did, and each added project is checked. Must-do projects come back at
1 from the LP, so step 1 keeps them. Nothing here proves the plan is the best one.

About a dozen lines.
