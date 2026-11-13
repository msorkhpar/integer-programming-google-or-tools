A city transit agency (invented for this practice) compares bus purchases by lifecycle cost. A bus
has a price paid now, a running cost (energy and maintenance) paid at the end of each year of its
life, some one-off costs in given years of its life (a battery replacement, say, in year 6), and a
resale value received at the end of its life. Everything is in $k of today's prices, and the
agency's real rate is `rate`.

Write `lifecycle_cost(price, running, life, rate, one_offs, resale)`, the bus's lifecycle cost on
today's date. `one_offs` is `{year of life: cost}`, with years counted from 1.

Write the lifecycle cost as one formula first, with each of its four terms. About six lines.
