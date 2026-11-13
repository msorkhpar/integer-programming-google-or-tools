A freight planner's tool can say whether a set of business rules can hold together, but it cannot
compute an IIS. Write the **deletion filter** (lesson 4.3.5) that turns that yes/no check into an
irreducible conflict, the same kind of answer `computeIIS` gives.

`deletion_filter(rules, feasible)` takes a list of rule names and a function `feasible(subset)` that
returns `True` when the rules in `subset` (a `set` of names) can all hold. Then:

1. If `feasible(set(rules))`, there is no conflict: return `[]`.
2. Otherwise keep a working set, starting with every rule. Go through the rules **in the given
   order**: remove the rule from the working set, and ask `feasible` about what is left. If it is
   still infeasible, the rule was not needed: leave it out. If it became feasible, the rule is part
   of the conflict: put it back.
3. Return the rules left in the working set, in the given order.

Each test runs on the working set as it stands, without the rules already left out; that is what
makes the result irreducible. No Gurobi license is needed. About ten lines.
