A gas utility's planning model takes one value per project and start year, and its reviewers check
every coefficient by hand. Write two functions in `values.py`:

- `yearly_pof(age, beta, eta)`: the probability that a main still in service at `age` fails within
  the next year, for a Weibull failure curve with survival function
  $`R(a) = e^{-(a/\eta)^\beta}`$.
- `start_year_npv(flows, start, base_year, escalation, rate, valuation_year)`: the NPV of a project
  started in year `start`. `flows[k]` is the amount of the project's $`k`$-th year (costs negative),
  quoted in `base_year` prices; it is paid in calendar year `start + k`, escalates at `escalation` a
  year from the base year, and is discounted at `rate` to `valuation_year`. Count every flow.

Write each formula with its exponents named before you code it: which year does each power count
from? About eight lines.
