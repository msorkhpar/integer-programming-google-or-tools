A regional water utility (invented for this practice) compares pipe projects at its board meeting.
Each project's forecast is a dictionary `{calendar year: amount}` in $k, costs negative and savings
positive, and some years have no entry at all. The board values every forecast on one date, the
start of `on_year`, at a yearly rate `rate`. An amount booked in year `y` is paid at the start of `y`.
Some forecasts start after the board's date; a few include money already paid in earlier years,
which the board carries forward to its date at the same rate.

Write `value_on(flows, rate, on_year)`, returning the forecast's value on that date.

Write the formula first, in the notation of the lesson: the value of an amount $`\text{CF}_y`$ on the
start of year $`y_0`$, and the sum over the forecast's years. Then check what it does for a year
before $`y_0`$ and for a gap between years. About four lines.
