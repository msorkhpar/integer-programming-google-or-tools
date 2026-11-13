# 5.1. Pyomo

Pyomo, an algebraic modeling language in Python: concrete models built from indexed Sets, Params,
Vars and Constraints, with lesson 6.4.1's multi-period GridCap model ported to it and checked
against MathOpt; solving with HiGHS and reading Pyomo's results objects, gaps, failed solves and
duals; Pyomo.GDP, which states a disjunction once and writes it as big-M rows or as the hull; and
Pyomo's piecewise-linear components and its tools for explaining an infeasible model.

The models this module ports come from section 6, which the course reaches later: the multi-period
timing model of lesson 6.4.1 (lessons 5.1.1, 5.1.2 and 5.1.4) and the outage disjunctions of lesson
6.2.4 (lesson 5.1.3). You do not need to have read them. Each lesson restates its model in full,
and where a lesson checks "the same numbers as lesson 6.4.1" (or 6.2.4), it compares with the
output that lesson recorded, which lesson 5.1.1 (and 5.1.3) shows on the page.

## Contents

1. [Concrete models with indexed Sets, Params, Vars and Constraints](README_5.1.1.md)
2. [Solving with HiGHS and reading results](README_5.1.2.md)
3. [Pyomo.GDP: disjunctions, big-M and hull transformations](README_5.1.3.md)
4. [Piecewise functions and the IIS tools](README_5.1.4.md)
