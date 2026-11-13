The vegetation team plans circuit work in three-year windows, and wants each pole line's risk of
failing *before the crew gets there*. The asset model hands over a Weibull curve per line (shape
`beta`, scale `eta` in years) and the line's age today. The line is in service today.

Write `pof_within(age, years, beta, eta)` in `risk.py`: the probability that a line of this age,
in service today, fails within the next `years` years. `cumulative(t, beta, eta)` (the Weibull
probability of having failed by age `t`) is already written for you.

Three to five lines.
