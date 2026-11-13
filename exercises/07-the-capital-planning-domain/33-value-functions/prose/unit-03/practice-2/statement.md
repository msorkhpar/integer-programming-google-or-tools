A city bus operator values its projects by rider-hours saved, accidents avoided and savings ($k). Its
board set swing ratings once (the biggest swing rated 100, the others as a share of it) against
references `old_reference`. Next year the planners redraw the swings: `new_reference` gives each
measure's new swing, in the same units. The board did not change its mind about what an accident or
a rider-hour is worth, only about how big the swings are.

Write `rerate(ratings, old_reference, new_reference)` in `swings.py`, returning ratings for the new
swings that keep the price of every measure in every other (`price`, given, computes one), and that
follow the convention again: the biggest swing is rated 100 and the others as a share of it.

Before coding, write down what a price is in terms of a rating, its reference and the ratings' total,
and ask which part may change. About three lines.
