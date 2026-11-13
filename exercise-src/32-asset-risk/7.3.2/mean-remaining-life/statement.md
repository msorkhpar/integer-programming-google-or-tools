A water utility's asset team budgets pump renewals on each pump's *mean* remaining life: the
average number of years still ahead, over all pumps of its kind that are working at its age. Each
kind's lifetimes follow a Weibull curve of shape `beta` and scale `eta` (years).

Write `mean_remaining_life(age, beta, eta)` in `pumps.py`. The survival function `survival(t)` is
written for you inside it, and `quad` from `scipy.integrate` is imported: `quad(g, a, math.inf)`
returns the area under `g` from `a` to infinity, and a bound on its error.

In the lesson's notation the mean remaining life at age $`a`$ is
$`\int_a^\infty R(u)\,du \,/\, R(a)`$. Decide what each part does before you code it: which area,
and why the division.

One numerical trap: for a very old pump, `survival(age)` is `exp` of a large negative number and
underflows to `0.0` (at age 200 with shape 3 and scale 20 it is $`e^{-1000}`$), so the area and the
divisor are both 0. Integrate the ratio instead,
$`R(u)/R(a) = \exp\big((a/\eta)^\beta - (u/\eta)^\beta\big)`$, which is the same quantity and never
forms the tiny number; the reference does that. The tests check your value with
`scipy.stats.weibull_min.expect`, and the old pump against its hazard. About three lines.
