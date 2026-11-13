# 3.3. Cuts, Presolve and Heuristics

What a MIP solver does besides branching. Branch-and-bound alone would explore far more of the search
tree than HiGHS or SCIP do on GridCap's models; three other parts of the solver make the difference.
Cutting planes add rows that bring the LP bound down without removing any plan. Presolve shrinks the
model before the search starts. Primal heuristics find good plans early, so the search can prune.
This module builds each of them by hand on GridCap portfolios, measures what the real solvers'
versions do on the five-year selection model, and ends by reading a complete HiGHS MIP log line by
line. GridCap is a fictional utility; its numbers are teaching data.

## Contents

1. [Cutting planes: Gomory and cover cuts by hand](README_3.3.1.md)
2. [Presolve: what the solver removes first](README_3.3.2.md)
3. [Primal heuristics: rounding, diving, RINS](README_3.3.3.md)
4. [Reading a full MIP log line by line](README_3.3.4.md)
