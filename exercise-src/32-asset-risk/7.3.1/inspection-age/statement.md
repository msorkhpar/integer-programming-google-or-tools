A rail operator keeps thousands of signal relays of a few types in service. Its maintenance rule
says: start inspecting a relay type once the failure rate of the relays of that type *still
working* reaches `rate` failures per relay per year. Each type's lifetimes follow a Weibull curve
with shape `beta` and scale `eta` (years), fitted by the operator's reliability team.

Write `trigger_age(rate, beta, eta)` in `relays.py`. It returns the age, in years, at which the
type's failure rate reaches `rate`. A type whose failure rate never rises with age gets `None`:
the rule should never trigger on age for it.

In the lesson's notation you are solving $`h(t) = \text{rate}`$ for $`t`$, with
$`h(t) = (\beta/\eta)(t/\eta)^{\beta - 1}`$. Solve it on paper first; then decide, from the
exponent $`\beta - 1`$, which shapes have no answer that means "the rate has risen to the limit."
The tests check your age against `scipy.stats.weibull_min` (`pdf / sf` at that age). Three to five
lines.
