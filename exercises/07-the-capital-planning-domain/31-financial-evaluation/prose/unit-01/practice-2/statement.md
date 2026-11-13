A port authority (invented for this practice) must protect a substation from flooding. One option
raises the equipment: a large cost now and a modest saving every year for decades. The other builds
a temporary barrier system: the same cost now, larger savings, but only for a few years. Finance has
not settled the discount rate, so the engineers want to know the rate at which the two options are
worth the same: below it one is better, above it the other.

Write `crossover_rate(a, b, low=0.0, high=1.0)`. `a` and `b` are lists of yearly amounts in $k,
the first one now (as `npv` in the file, which matches numpy-financial's). They may have different
lengths. Between `low` and `high` the two values are equal at exactly one rate, and on either side of
it one option is better; you are not told which one is better below it. Return that rate, to within
a millionth.

State in symbols what function of the rate is zero at the answer before you code it. About ten
lines, a loop that halves an interval.
