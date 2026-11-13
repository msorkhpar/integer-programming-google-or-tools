# 5.4. Choosing a Solver

Which solver should a service use, and how do you show it? The seven solvers a team is likely to
weigh, and the four that run in the course runner; benchmarks that someone else could repeat, built
on an instance set, several seeds, one gap target and the shifted geometric mean; what each solver
costs and what it needs inside a container; and the recommendation memo that turns all of it into a
decision with a fallback and the conditions that would reopen it.

The benchmark runs the one-period selection model, which lesson 5.4.1 states in full. Two lessons
also name models from section 6, which the course reaches later: lesson 5.4.3 counts the variables
and rows of the start-year (timing) model of lesson 6.4.2, and lessons 5.4.1 and 5.4.4 use the
continuous carry-over variable of lesson 6.4.4 as their example of a continuous variable. You do not
need to have read those lessons: each page says what it takes from them, and no lesson here checks
its numbers against a section 6 lesson's output.

## Contents

1. [The landscape: Gurobi, CPLEX, Xpress, HiGHS, SCIP, CBC, CP-SAT](README_5.4.1.md)
2. [Honest benchmarking: instance sets, seeds, time-to-gap, shifted geometric mean](README_5.4.2.md)
3. [License cost and fit for containers](README_5.4.3.md)
4. [Writing a solver recommendation](README_5.4.4.md)
