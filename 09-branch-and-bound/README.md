# 3.2. Branch and Bound

How a MILP solver finds the best yes/no plan without trying every plan. It solves the LP with the
yes/no rule dropped, picks a variable whose LP value is a fraction, and splits the problem in two:
one copy where that variable is 0 and one where it is 1. Repeating the split builds a tree. The
search keeps the best plan found so far and throws away every branch whose LP value says it cannot
do better. This module builds that search on GridCap's tiny and small portfolios, with GLOP solving
the LP at every node, compares the rules for which node and which variable to take next, and ends
with a complete knapsack branch-and-bound in about 120 lines of plain Python, checked against brute
force and HiGHS.

## Contents

1. [Branching on a fractional variable](README_3.2.1.md)
2. [Bounds, incumbents and pruning](README_3.2.2.md)
3. [Node and variable selection](README_3.2.3.md)
4. [A knapsack branch-and-bound in 116 lines](README_3.2.4.md)
