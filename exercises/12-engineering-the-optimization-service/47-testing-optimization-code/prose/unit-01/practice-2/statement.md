A tree-trimming contractor's planning model has a crew rule, and the rule has no tests. Jobs take
one or more years of work and use a given number of crew-months in each of those years; each year
has a fixed number of crew-months. With $`x_{j,s} = 1`$ when job $`j`$ starts in year $`s`$, and
$`m_{j,k}`$ the crew-months job $`j`$ uses in its $`k`$-th year of work ($`k = 0, 1, \dots`$):

```math
\sum_{j} \; \sum_{s \in T_j,\; 0 \le y - s < |m_j|} m_{j,\,y-s}\, x_{j,s} \;\le\; K_y \qquad \forall y \in \{2027, 2028, 2029\} \qquad \text{(crews}_y)
```

Your job is not to write the rule but to write the cases that test it. `cases()` returns a list of
hand-made cases `(jobs, crews, plan, allowed)`; the comments in `crew_cases.py` give each field's
shape. Each case should be small enough to check by eye: one or two jobs, and crew numbers chosen so
that the crew rule decides.

The tests build a model with the crew rule alone for each case, fix the plan, and check your
verdict, so every verdict must be the correct rule's, and your cases must hold at least one allowed
and one refused plan. Then they run your cases against three wrong versions of the rule, each a
mistake real code makes, and some case must catch each one, that is, get a different verdict from
it than the one you wrote:

- a rule written as if the limit were strict, so a year may use at most $`K_y - 1`$ crew-months;
- a rule whose loop over the years stops one year early, so 2029 is never checked;
- a rule that charges all of a job's crew-months to the year it starts.

Write the cases. About five lines.
