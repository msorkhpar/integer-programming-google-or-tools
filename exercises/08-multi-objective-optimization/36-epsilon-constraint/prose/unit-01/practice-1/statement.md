A county parks district picks which trail projects to fund this year. Each project brings visitors
(people per year) and protects habitat (acres), and each has a cost; the year's budget caps the
total cost. The parks board has pledged to protect at least `habitat_floor` acres this year, and
within that pledge it wants as many visitors as possible.

Write `most_visitors(trails, budget, habitat_floor)` in `trails.py`. It returns the names of the
funded trails as a sorted tuple, or `None` when no affordable choice meets the pledge. Build the
model with MathOpt and solve it with HiGHS (the starter has the solve call and the reading of the
answer).

Write the formulation first: the set of trails, the parameters with their units, the decision
variables with their domains, the objective with its sense, and every constraint with a label.
Then code it.

The tests compare your answer with every affordable choice listed by hand, on their own small
instances, so any correct formulation passes. About eight lines.
