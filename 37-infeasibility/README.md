# 9.1. Infeasibility

When a run comes back with no plan: telling infeasible from unbounded from "the solver ran out of
time", catching the common data errors before any solve, finding the rules that clash with an IIS
(MathOpt with a filter, gurobipy, Pyomo), pricing the smallest repair with elastic constraints and
`feasRelax`, using CP-SAT's assumptions to list conflicts cheaply, and writing it all up as a
message a planner can act on. Every lesson works on one GridCap Budget Lock scenario with three
conflicts. GridCap is a fictional utility's portfolio.

## Contents

1. [Infeasible, unbounded, or the solver can't tell](README_9.1.1.md)
2. [Validating inputs before the solve](README_9.1.2.md)
3. [IIS with MathOpt, gurobipy and Pyomo](README_9.1.3.md)
4. [Elastic constraints and feasibility relaxation](README_9.1.4.md)
5. [CP-SAT assumptions as a conflict finder](README_9.1.5.md)
6. [Turning an IIS into a planner message](README_9.1.6.md)
