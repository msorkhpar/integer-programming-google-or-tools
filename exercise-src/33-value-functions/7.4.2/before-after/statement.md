A hospital group replaces imaging machines. For each candidate the clinical engineers record three
measures with the old machine (`before`) and with its replacement (`after`): hours of downtime a
year and energy used, where lower is better, and scans a day, where higher is better
(`HIGHER_IS_BETTER` says which is which). Each measure has a reference (the swing the board agreed
on, in the measure's own unit) and a weight.

Write `improvement(measure, before, after)`, how much better a measure gets, so that more is always
better, and `project_score(project, reference, weights)`, the weighted sum of each improvement as a
share of its reference. `plan_score` (given) adds the scores of the projects a plan funds; the tests
call both.

The board will compare plans of different sizes by their total score, so be careful what a score of 0
means. A replacement that makes one measure worse (a new machine that uses more energy) should lose
score for it, and the loss is not capped. About four lines.
