A district-heating company's analytics team predicts, for every pump, the number of years `r` by
which there is a chance `q` that a pump working today at age `age` will have failed. Most reports
use `q = 0.1`, the P10 remaining life, because the crews plan to it; a few use the median,
`q = 0.5`. The reliability team supplies one shape `beta` per pump type. The risk model needs a
whole curve per pump.

Write `scale_from_report(age, r, q, beta)` in `calibrate.py`: the scale `eta` (years) of the
Weibull curve with shape `beta` on which a pump working at `age` has exactly the chance `q` of
failing within the next `r` years.

The lesson solved this for the median. Write the condition for a general `q` in its notation,
$`R(a + r)/R(a) = 1 - q`$, and solve it for $`\eta`$ before you code. The tests check the curve you
return with `scipy.stats.weibull_min`. One or two lines.
