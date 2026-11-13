A transmission company runs a fleet of circuit breakers of one type, with Weibull shape `beta`
and scale `eta` (years). A failed breaker is repaired and put back without being made any younger,
so it can fail again. The maintenance shop sizes its spares from the fleet's expected failures in
each of the coming years.

Write two functions in `breakers.py`:

- `failures_by_year(ages, beta, eta, years)`: a list of `years` numbers, the whole fleet's expected
  failures in the coming year, the year after, and so on; `ages` are the breakers' ages today;
- `chance_of_none(age, beta, eta, years)`: the chance that one breaker, working today at `age`,
  has no failure at all in the next `years` years.

Write both in the lesson's notation first, with $`\Lambda(t) = (t/\eta)^\beta`$. The tests compare
with `scipy.stats.weibull_min.logsf`, whose negative is $`\Lambda`$. About seven lines.
