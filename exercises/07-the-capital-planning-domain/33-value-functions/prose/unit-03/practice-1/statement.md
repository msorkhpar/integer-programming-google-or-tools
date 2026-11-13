A water utility's board weighs three measures for its main renewals: breaks avoided, leakage
avoided (megalitres) and operating savings ($k). Each has a reference swing, from no benefit to the
amount in `REFERENCE`. The board follows the group procedure of swing weighting: every member writes
down a private rating of each measure's swing against the biggest one, and the board then settles on
the **middle** rating of its members for each measure (the median, which for an even number of
members is halfway between the two middle ratings), so that one member at an extreme cannot drag
the result.

Write `panel_weights(ratings)` in `panel.py`, where `ratings[measure]` lists the members' ratings,
returning the weights. Then write `price(weights, reference, measure, base)`: how many units of
`base` the weights say one unit of `measure` is worth, so the board can read its weights as prices
("one break avoided is worth $125k").

Work the first test's weights by hand before coding. About five lines.
