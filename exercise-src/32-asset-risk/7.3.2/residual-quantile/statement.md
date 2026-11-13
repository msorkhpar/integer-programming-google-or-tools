A wind farm books a crane months ahead to swap a turbine's gearbox, and wants to book it before the
gearbox's chance of failing climbs too high. For a gearbox that is working today at age `age`,
with a Weibull curve of shape `beta` and scale `eta` (years), the farm asks: how many years from
today until the chance that it has failed reaches `q`? With `q = 0.1` that is the gearbox's P10
remaining life.

Write `years_until(age, q, beta, eta)` in `gearbox.py`.

In the lesson's notation the chance of still working $`r`$ years from now, given working today, is
$`R(a + r)/R(a)`$. Set it to $`1 - q`$, write it out with $`R(t) = e^{-(t/\eta)^\beta}`$, and solve
for $`r`$ on paper first. The tests check your answer with `scipy.stats.weibull_min`. One or two
lines.
