An electricity regulator (invented for this practice) asks every utility to report present values
in constant dollars of a base year: amounts deflated to base-year prices and discounted at a real
rate. The utility's own forecasts are nominal (each amount in the prices of the year it is paid),
and its finance team works with a nominal discount rate. General inflation is `inflation` a year.

Write `constant_dollar_value(forecast, nominal_rate, inflation, base_year)`. `forecast` is
`{calendar year: nominal amount}` in $k, paid at the start of each year, and the value is on the
start of `base_year`. Your answer must agree with the finance team's nominal value of the same
forecast; the regulator only wants it reached in constant dollars.

Write two formulas first: an amount in base-year dollars, and the real rate that matches the
nominal one. About six lines.
