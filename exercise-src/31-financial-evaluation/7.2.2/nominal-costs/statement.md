A gas distribution company (invented for this practice) prices main replacement from a price book
compiled in `price_year`. A job's estimate is a tuple of yearly amounts in $k, one per year of work,
all at price-book prices. The contractor bills each year's work at the prices of the year it is
done, and the contract says prices rise by `escalation` a year.

Write `billed(estimate, price_year, start, escalation)`, returning `{calendar year: amount billed}`
for a job that starts in `start`. The job may start in the price-book year or later.

Write the formula for the amount billed in calendar year $`y`$ first, and say what its exponent counts
from. About four lines.
