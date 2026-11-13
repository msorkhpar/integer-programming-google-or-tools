The practice utility's board scores its projects on three measures instead of GridCap's two: NPV
($k), risk removed ($k) and customer-minutes of outage avoided. You receive one table per measure,
keyed `(project id, start year)` like every coefficient table of milestone 3, and must fold them
into one value per start that the model can maximize.

The board has fixed, before any project was scored, a **reference** $`R_k`$ for each measure (the
swing from no benefit to this much, in the measure's own unit) and a **swing rating** $`s_k`$ for each
(the biggest swing gets 100). The weights and the value are

```math
w_k = \frac{s_k}{\sum_j s_j}, \qquad v_{i,t} = \sum_k w_k\,\frac{m_{k,i,t}}{R_k}
```

so $`m/R`$ has no unit, zero means no benefit, and a project's value does not depend on which other
projects are candidates (lessons 7.4.2 and 7.4.3). Restating a measure in other units together with
its reference must change nothing (lesson 7.4.4).

Write, in `value.py`:

- `weights(ratings)`: the formula above.
- `value_table(measures, reference=REFERENCE, ratings=RATINGS)`: `{(i, t): v}` over every key found
  in any measure's table (a missing entry counts as 0), each value rounded to 6 decimals. Use the
  `reference` it is given.
- `ranking(table)`: every key, highest value first; equal values in key order, so two runs always
  list them the same way.
