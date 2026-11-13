A pipeline operator (invented for this practice) hired a consultant to value a compressor upgrade
for each year it could start. The consultant's table `{start year: value}` in $k gives each entry
valued at the start of its own start year, "as if that year were today". The operator's planning
model needs every entry on one date, the start of `plan_year`, at the yearly rate `rate`. Some
tables include starts earlier than `plan_year` (for a re-plan of work already under way).

Write `to_plan_date(values_at_start, rate, plan_year)`, returning the table on the plan's date.

Say in one sentence what an entry valued "at its own start" is missing, then write the conversion
as a formula. About four lines.
