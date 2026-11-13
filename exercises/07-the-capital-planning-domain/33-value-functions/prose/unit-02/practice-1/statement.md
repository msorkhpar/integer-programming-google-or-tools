A city's transit agency ranks bus-stop upgrades by three measures: rider time saved, complaints
avoided and operating savings. The data comes from three teams, and each records amounts in the unit
it likes: rider time in minutes or hours, complaints one by one or by the dozen, savings in dollars
or thousands of dollars. Every amount arrives as a pair `(amount, unit)`, and so does each measure's
reference, the swing the agency's board agreed on. `UNITS` and `in_base` (given) say what each unit
measures and how many base units it is.

Write `score(benefit, reference, weights)` in `stops.py`: the weighted sum, over the measures, of
the benefit as a share of its reference. Then write `rank(projects, reference, weights)`, the project
names from the highest score to the lowest, with equal scores in name order so that the list is the
same on every run.

A team switching from hours to minutes, or the board restating a reference in dollars instead of
$k, has not changed anyone's mind about any project, so it must not change any score. About eight
lines.
