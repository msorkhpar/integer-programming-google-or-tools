A water utility renews old cast-iron mains. Its asset team models each main's breaks with a Weibull
curve, the way GridCap models failures: `breaks(age, beta, eta, years)` (given) is the expected number
of breaks between ages `age` and `age + years` if the main is only repaired when it breaks. One
break leaves `households` households without water for `hours` hours.

A renewal of **depth** `depth` makes the main as old as `(1 - depth)` times its age when the
renewed main goes into service: 1 is a new pipe, 0.5 a relining. The work starts in year `start` and
takes `duration` whole years (0 for a job finished within its first year), so the renewed main is in
service from `start + duration`. Until then the old main keeps aging and breaking. `main.age` is its
age in `first_year`, the first year of the plan, and benefits are counted over a window of `window`
years from `first_year`.

Write `benefit(main, depth, start, duration, first_year, window)` in `mains.py`, returning the
expected breaks avoided within the window and the household-hours without water they would have
cost: `{"breaks": ..., "household_hours": ...}`. Work that goes into service at or after the end of
the window avoids nothing.

Write the formula for the breaks avoided before you code it: which age goes in, and how many years
are left? About eight lines.
