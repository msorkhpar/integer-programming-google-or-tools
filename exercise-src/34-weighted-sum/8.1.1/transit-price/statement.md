A city transit agency can upgrade some of its bus depots this year. Each upgrade costs money and
brings two benefits: more daily riders (better service from the depot) and less CO2 a year (electric
buses charged there). The data team stores CO2 in kilograms a year, as the meters report it. After
a long meeting the agency's board settled its trade-off in one sentence: "cutting one tonne of CO2 a
year is worth as much to us as `riders_per_tonne` extra daily riders."

Write `weighted_choice(upgrades, budget, riders_per_tonne)` in `depots.py`: the set of upgrade names
to fund, at most once each, with total cost within `budget`, that is best by the board's own
trade-off. The model's variables and the budget row are written; the objective is yours.

Write the objective first, in notation: with $`U`$ the upgrades, $`x_u \in \{0, 1\}`$ whether
upgrade $`u`$ is funded, $`r_u`$ its riders, $`g_u`$ its CO2 cut in kg and $`\pi`$ the board's
price, what are the two weights, and in which units is each term? Then code it.

About one line.
