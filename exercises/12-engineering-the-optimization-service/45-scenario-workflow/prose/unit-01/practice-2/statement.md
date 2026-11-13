Riverbend Water (invented for this practice) plans its main-replacement program with `Plan`
records. Besides a yearly budget, a plan holds, for each district, a list with the number of crews
available in each month, and a list of tags. Analysts copy a plan to try a storm-reserve variant,
then change budgets and individual months in the copy.

Write `copy_plan(p, plan_id, name, by)` in `plan.py`. It returns a new `Plan` with the given id,
name and author, inputs equal to `p`'s, and `parent_id` naming `p`. Nothing the copy holds may be
an object that `p` also holds, at any depth, so that no edit to the copy, however deep, can change
`p`. About four lines.
